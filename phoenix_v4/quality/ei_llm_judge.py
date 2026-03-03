"""
LLM judge for EI tie-break when multiple candidates tie on composite score.

Uses JSONL cache: load_cache_line returns last match (last write wins),
append_cache_line for persistence.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from phoenix_v4.quality.ei_adapter import EICandidate


@dataclass
class LLMJudgeResult:
    """Result of LLM tie-break judgment."""
    chosen_id: Optional[str]
    rationale: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


def load_cache_line(cache_path: Path, cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Load from JSONL cache. Returns the last matching entry (last write wins).
    """
    if not cache_path or not cache_path.exists():
        return None
    last_match: Optional[Dict[str, Any]] = None
    key_str = str(cache_key)
    with open(cache_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("cache_key") == key_str:
                    last_match = obj
            except json.JSONDecodeError:
                continue
    return last_match


def append_cache_line(cache_path: Path, entry: Dict[str, Any]) -> None:
    """Append a single JSONL line to the cache file."""
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def build_llm_judge_prompt(
    thesis: str,
    candidates: List[EICandidate],
    cfg: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build the prompt for LLM tie-break judgment.
    """
    cfg = cfg or {}
    intro = cfg.get("intro", "You are judging which candidate best aligns with the thesis.")
    thesis_block = f"Thesis:\n{thesis}\n\n"
    candidates_block = "Candidates:\n"
    for i, c in enumerate(candidates, 1):
        candidates_block += f"{i}. [ID: {c.atom_id}]\n{c.text[:500]}{'...' if len(c.text) > 500 else ''}\n\n"
    instructions = cfg.get(
        "instructions",
        "Return JSON with 'chosen_id' (the atom_id of the best candidate) and 'rationale' (brief explanation).",
    )
    return f"{intro}\n\n{thesis_block}{candidates_block}{instructions}"


def judge_tie_break(
    thesis: str,
    candidates: List[EICandidate],
    call_llm_json: Callable[..., Any],
    cfg: Optional[Dict[str, Any]] = None,
    cache_path: Optional[Path] = None,
    cache_key: Optional[str] = None,
) -> Optional[LLMJudgeResult]:
    """
    Use LLM to pick the best candidate among ties.
    Returns LLMJudgeResult with chosen_id and rationale, or None on failure.
    """
    cfg = cfg or {}
    if not candidates:
        return None

    if len(candidates) == 1:
        return LLMJudgeResult(chosen_id=candidates[0].atom_id, rationale="Single candidate")

    # Check cache
    if cache_path and cache_key:
        cached = load_cache_line(cache_path, cache_key)
        if cached and cached.get("chosen_id"):
            return LLMJudgeResult(
                chosen_id=cached["chosen_id"],
                rationale=cached.get("rationale"),
                raw_response=cached,
            )

    prompt = build_llm_judge_prompt(thesis, candidates, cfg)
    try:
        response = call_llm_json(prompt, cfg=cfg)
        if isinstance(response, dict):
            chosen_id = response.get("chosen_id")
            rationale = response.get("rationale")
        elif isinstance(response, str):
            try:
                parsed = json.loads(response)
                chosen_id = parsed.get("chosen_id")
                rationale = parsed.get("rationale")
            except json.JSONDecodeError:
                return None
        else:
            return None

        result = LLMJudgeResult(
            chosen_id=chosen_id,
            rationale=rationale,
            raw_response=response if isinstance(response, dict) else {"raw": response},
        )

        if cache_path and cache_key and chosen_id:
            append_cache_line(cache_path, {
                "cache_key": str(cache_key),
                "chosen_id": chosen_id,
                "rationale": rationale,
                "thesis_preview": thesis[:200],
                "candidate_ids": [c.atom_id for c in candidates],
            })

        return result
    except Exception:
        return None
