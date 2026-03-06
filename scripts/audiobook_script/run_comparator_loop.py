#!/usr/bin/env python3
"""
Qwen-Only Audiobook Comparator Loop — run_comparator_loop.py

Pipeline: English source → Qwen draft → Judge → [repair loop] → pass or manual_review.
No human in the loop at any stage. All prompt patch application, routing, and artifact
persistence are fully automated.

Architecture:
  - Section-level parallelism: asyncio.gather + Semaphore(max_parallel_sections)
    Sections within a book are embarrassingly parallel; loops within a section are sequential.
  - Within a section: Qwen draft → judge → PatchApplier → rerun (max max_loops times).
  - Patch injection: judge-returned prompt_patches assembled automatically by PatchApplier;
    appended to system prompt as REVISION INSTRUCTIONS block, hard gate patches first.
  - Manual review: sections exhausting max_loops without passing write a full review packet
    (best_draft, final_draft, defect_history, review_summary, status.json) and are added
    to the global manual_review_queue.json for PhoenixControl UI visibility.
  - Judge independence: separate system prompt ID, temperature 0.1, rotated seed per loop.
    Judge output is JSON-schema validated (schemas/comparator_result_v2.schema.json).
    Schema fail → manual_review; never silent pass.

Config: config/audiobook_script/comparator_config.yaml
Checklist: config/audiobook_script/comparison_checklist_v2.yaml
Schema: schemas/comparator_result_v2.schema.json
Rubric: config/audiobook_script/static_polish_rubric.yaml

Usage:
  # Single section (debug/test)
  python scripts/audiobook_script/run_comparator_loop.py \\
    --section-id intro_001 --locale zh-TW \\
    --english-source artifacts/audiobook/source/intro_001.txt \\
    --book-id book_abc --batch-id batch_20260306

  # Full book (parallel sections)
  python scripts/audiobook_script/run_comparator_loop.py \\
    --book-id book_abc --batch-id batch_20260306 \\
    --sections-manifest artifacts/audiobook/source/book_abc/manifest.json \\
    --locale zh-TW

  # Full batch (parallel books × parallel sections)
  python scripts/audiobook_script/run_comparator_loop.py \\
    --batch-id batch_20260306 \\
    --batch-manifest artifacts/audiobook/source/batch_20260306/manifest.json

  # Regression set validation
  python scripts/audiobook_script/run_comparator_loop.py \\
    --regression-run \\
    --golden-set config/audiobook_script/golden_regression_set/

Authority: config/audiobook_script/comparator_config.yaml (all parameters).
           docs/GO_LIVE_FINAL_CHECKLIST.md (go-live requirements).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("comparator_loop")

# ─── CONFIG LOADING ───────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("Failed to load YAML %s: %s", path, e)
        return {}


def _load_config(repo: Path) -> dict:
    cfg_path = repo / "config" / "audiobook_script" / "comparator_config.yaml"
    cfg = _load_yaml(cfg_path)
    if not cfg:
        raise RuntimeError(f"comparator_config.yaml missing or empty at {cfg_path}")
    # Validate max_loops range (schema enforcement)
    max_loops = cfg.get("loop_control", {}).get("max_loops", 3)
    if not (1 <= max_loops <= 5):
        raise ValueError(f"max_loops={max_loops} is outside allowed range [1, 5] — see comparator_config.yaml")
    return cfg


def _load_checklist(repo: Path) -> dict:
    cl_path = repo / "config" / "audiobook_script" / "comparison_checklist_v2.yaml"
    return _load_yaml(cl_path)


def _load_result_schema(repo: Path) -> dict:
    schema_path = repo / "schemas" / "comparator_result_v2.schema.json"
    if not schema_path.exists():
        raise RuntimeError(f"Result schema missing: {schema_path}")
    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)

# ─── DATA STRUCTURES ─────────────────────────────────────────────────────────

@dataclass
class GateResult:
    gate_id: str
    pass_: bool              # 'pass' is reserved; use pass_
    checklist_schema_version: str
    loop_index: int
    section_id: str
    locale: str
    gate_type: str = "hard"
    score: float | None = None
    weight: float | None = None
    defect: str | None = None
    prompt_patch: str | None = None
    rubric_rules_failed: list[str] | None = None
    judge_confidence: float | None = None
    timestamp_utc: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d


@dataclass
class LoopTrace:
    """Full artifact trace for one loop pass."""
    run_id: str
    batch_id: str
    book_id: str
    section_id: str
    locale: str
    loop_index: int
    input_draft_hash: str
    prompt_patch: str                  # assembled patch block (empty str for loop 1)
    rerun_prompt_hash: str             # SHA-256 of patched system prompt for NEXT loop
    aggregate_score: float
    hard_gates_passed: bool
    final_decision: str                # "pass" | "continue" | "manual_review"
    timestamp_utc: str
    gate_results: list[dict] = field(default_factory=list)


@dataclass
class SectionResult:
    section_id: str
    locale: str
    book_id: str
    batch_id: str
    decision: str                      # "pass" | "manual_review"
    loops_attempted: int
    best_loop_index: int
    best_aggregate_score: float
    best_draft: str
    final_draft: str
    loop_traces: list[LoopTrace] = field(default_factory=list)
    error: str | None = None

# ─── HASH UTILITIES ──────────────────────────────────────────────────────────

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).digest().hex()


def _section_seed(section_id: str, locale: str) -> int:
    """Deterministic draft seed: same section+locale always produces the same seed."""
    raw = f"{section_id}:{locale}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16)


def _judge_seed(section_id: str, loop_index: int) -> int:
    """Rotated judge seed: different per loop to prevent anchoring, deterministic for replay."""
    raw = f"{section_id}:loop{loop_index}:JUDGE_SALT_V2"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16)

# ─── QWEN API STUB ───────────────────────────────────────────────────────────
# Replace with real Qwen Cloud (Dashscope) API calls.
# Draft uses temperature=0.7, seed=section_hash.
# Judge uses temperature=0.1, seed=rotated, separate system_prompt_id.

async def _call_qwen_draft(
    section_text: str,
    locale: str,
    system_prompt: str,
    cfg: dict,
    seed: int,
) -> str:
    """
    Async call to Qwen draft model. Returns draft text string.
    In production: POST to Dashscope /compatible-mode/v1/chat/completions
    with model_id=qwen-max, temperature=0.7, seed=seed.
    """
    draft_cfg = cfg.get("draft_model", {})
    # TODO: replace with real API call
    # response = await dashscope_client.chat(
    #     model=draft_cfg["model_id"],
    #     messages=[{"role": "system", "content": system_prompt},
    #               {"role": "user", "content": section_text}],
    #     temperature=draft_cfg.get("temperature", 0.7),
    #     seed=seed,
    #     max_tokens=draft_cfg.get("max_output_tokens", 3000),
    # )
    # return response.choices[0].message.content
    raise NotImplementedError(
        "Implement Qwen draft API call (Dashscope). "
        "See config/audiobook_script/comparator_config.yaml > draft_model."
    )


async def _call_qwen_judge(
    english_source: str,
    draft: str,
    locale: str,
    judge_system_prompt: str,
    cfg: dict,
    seed: int,
) -> str:
    """
    Async call to Qwen judge model. Returns raw JSON string.
    Uses temperature=0.1, separate system prompt, rotated seed.
    Must return JSON conforming to schemas/comparator_result_v2.schema.json.
    """
    judge_cfg = cfg.get("judge_model", {})
    # TODO: replace with real API call
    raise NotImplementedError(
        "Implement Qwen judge API call (Dashscope). "
        "See config/audiobook_script/comparator_config.yaml > judge_model."
    )

# ─── SCHEMA VALIDATION ────────────────────────────────────────────────────────

def _validate_judge_output(raw_json: str, result_schema: dict, checklist_version: str) -> tuple[bool, list[dict] | None, str]:
    """
    Validate judge JSON output against comparator_result_v2.schema.json.
    Also verifies checklist_schema_version binding.
    Returns (valid: bool, gate_results: list|None, error_msg: str).
    Schema fail → manual_review; never silent pass.
    """
    try:
        gate_results = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, None, f"Judge output is not valid JSON: {e}"

    if not isinstance(gate_results, list):
        return False, None, "Judge output must be a JSON array"

    # Validate checklist_schema_version binding on all items
    for item in gate_results:
        item_ver = item.get("checklist_schema_version", "")
        if not item_ver.startswith("2.0"):
            return False, None, (
                f"checklist_schema_version mismatch: got '{item_ver}', "
                f"expected '2.0.x' (bound to comparison_checklist_v2.yaml schema_version=2.0)"
            )

    try:
        import jsonschema
        for item in gate_results:
            # jsonschema uses "pass" not "pass_"; the judge output uses "pass"
            jsonschema.validate(instance=item, schema=result_schema["definitions"]["GateResult"])
    except ImportError:
        # jsonschema not installed: basic structural check only
        required = {"gate_id", "pass", "checklist_schema_version", "loop_index", "section_id", "locale"}
        for item in gate_results:
            missing = required - set(item.keys())
            if missing:
                return False, None, f"Gate result missing required fields: {missing}"
    except Exception as e:
        return False, None, f"Schema validation failed: {e}"

    return True, gate_results, ""

# ─── PATCH APPLIER ────────────────────────────────────────────────────────────

class PatchApplier:
    """
    Assembles judge-returned prompt_patches into the next Qwen system prompt.
    Fully automated — no human reviews the patch before injection.

    Assembly order:
      1. Original system prompt (unchanged)
      2. REVISION INSTRUCTIONS header
      3. Hard gate patches first (sorted by gate_id for determinism)
      4. Scored gate patches (sorted by weight descending)

    Each patch is labeled with [HARD — must fix] or [IMPROVE] prefix.
    The assembled patch block is capped at max_patch_tokens characters
    (scored patches truncated before hard patches if overflow).
    """

    def __init__(self, cfg: dict, checklist: dict) -> None:
        self.cfg = cfg.get("patch_injection", {})
        self.max_patch_chars = self.cfg.get("max_patch_tokens", 600) * 4  # ~4 chars/token
        self.hard_prefix = self.cfg.get("hard_gate_prefix", "[HARD — must fix]")
        self.scored_prefix = self.cfg.get("scored_gate_prefix", "[IMPROVE]")
        self.header_template = self.cfg.get(
            "revision_block_header",
            "## REVISION INSTRUCTIONS (Loop {loop_index})\n## Fix ALL issues below before producing the draft.\n"
        )
        # Build weight lookup from checklist
        self._gate_weights: dict[str, float] = {}
        self._gate_types: dict[str, str] = {}
        for gate in (checklist.get("gates") or []):
            gid = gate.get("gate_id", "")
            self._gate_weights[gid] = gate.get("weight", 1.0)
            self._gate_types[gid] = gate.get("type", "hard")

    def assemble(self, original_system_prompt: str, gate_results: list[dict], loop_index: int) -> str:
        """Return patched system prompt for next loop."""
        failed = [g for g in gate_results if not g.get("pass", True) and g.get("prompt_patch")]

        if not failed:
            return original_system_prompt

        hard_patches = sorted(
            [g for g in failed if self._gate_types.get(g["gate_id"], "hard") == "hard"],
            key=lambda g: g["gate_id"]
        )
        scored_patches = sorted(
            [g for g in failed if self._gate_types.get(g["gate_id"], "hard") == "scored"],
            key=lambda g: -self._gate_weights.get(g["gate_id"], 1.0)
        )

        header = self.header_template.format(loop_index=loop_index)
        patch_lines: list[str] = []

        for g in hard_patches:
            defect_ctx = f" [Defect: {g['defect']}]" if (
                self.cfg.get("include_defect_in_patch") and g.get("defect")
            ) else ""
            patch_lines.append(f"{self.hard_prefix} {g['gate_id']}{defect_ctx}: {g['prompt_patch']}")

        for g in scored_patches:
            defect_ctx = f" [Defect: {g['defect']}]" if (
                self.cfg.get("include_defect_in_patch") and g.get("defect")
            ) else ""
            patch_lines.append(f"{self.scored_prefix} {g['gate_id']}{defect_ctx}: {g['prompt_patch']}")

        patch_block = header + "\n".join(patch_lines)

        # Cap patch block: always keep hard patches; trim scored if overflow
        overflow_strategy = self.cfg.get("on_patch_overflow", "truncate_scored_keep_hard")
        if len(patch_block) > self.max_patch_chars and overflow_strategy == "truncate_scored_keep_hard":
            hard_block = header + "\n".join(
                f"{self.hard_prefix} {g['gate_id']}: {g['prompt_patch']}" for g in hard_patches
            )
            patch_block = hard_block[:self.max_patch_chars]
            logger.warning("Patch block truncated (kept hard gates only); loop=%d", loop_index)

        return original_system_prompt + "\n\n" + patch_block

# ─── SCORE AGGREGATION ────────────────────────────────────────────────────────

def _aggregate_score(gate_results: list[dict], checklist: dict) -> tuple[float, bool]:
    """
    Returns (aggregate_score: float, all_hard_passed: bool).
    aggregate_score = scored_total / max_scored_total.
    all_hard_passed = True only if every hard gate has pass=True.
    """
    gate_map = {g["gate_id"]: g for g in (checklist.get("gates") or [])}
    scored_total = 0.0
    max_scored_total = 0.0
    all_hard_passed = True

    for result in gate_results:
        gid = result.get("gate_id", "")
        gate_def = gate_map.get(gid, {})
        gtype = gate_def.get("type", "hard")
        passed = result.get("pass", False)

        if gtype == "hard":
            if not passed:
                all_hard_passed = False
        else:
            weight = gate_def.get("weight", 1.0)
            score = result.get("score") or 0.0
            scored_total += score * weight
            max_scored_total += weight

    agg = (scored_total / max_scored_total) if max_scored_total > 0 else 1.0
    return round(agg, 4), all_hard_passed


def _passes_threshold(aggregate_score: float, all_hard_passed: bool, cfg: dict, locale: str) -> bool:
    """A section passes if all hard gates pass AND aggregate_score >= threshold."""
    if not all_hard_passed:
        return False
    scoring = cfg.get("scoring", {})
    base_threshold = scoring.get("min_scored_pass_threshold", 0.75)
    locale_overrides = cfg.get("locale_threshold_overrides", {})
    locale_cfg = locale_overrides.get(locale, {})
    threshold = locale_cfg.get("min_scored_pass_threshold", base_threshold)
    return aggregate_score >= threshold

# ─── ARTIFACT PERSISTENCE ─────────────────────────────────────────────────────

def _artifact_dir(repo: Path, cfg: dict, batch_id: str, book_id: str, section_id: str, loop_index: int) -> Path:
    base = repo / cfg.get("artifact_trace", {}).get("base_path", "artifacts/audiobook")
    return base / batch_id / book_id / section_id / f"loop_{loop_index}"


def _write_loop_trace(repo: Path, cfg: dict, trace: LoopTrace) -> None:
    artifact_cfg = cfg.get("artifact_trace", {})
    d = _artifact_dir(repo, cfg, trace.batch_id, trace.book_id, trace.section_id, trace.loop_index)
    d.mkdir(parents=True, exist_ok=True)
    trace_data = {
        "run_id": trace.run_id,
        "batch_id": trace.batch_id,
        "book_id": trace.book_id,
        "section_id": trace.section_id,
        "locale": trace.locale,
        "loop_index": trace.loop_index,
        "input_draft_hash": trace.input_draft_hash,
        "prompt_patch": trace.prompt_patch,
        "rerun_prompt_hash": trace.rerun_prompt_hash,
        "aggregate_score": trace.aggregate_score,
        "hard_gates_passed": trace.hard_gates_passed,
        "final_decision": trace.final_decision,
        "timestamp_utc": trace.timestamp_utc,
        "gate_results": trace.gate_results,
    }
    (d / "trace.json").write_text(json.dumps(trace_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # JSONL observability log (append)
    jsonl_path = repo / artifact_cfg.get("jsonl_log_path", "artifacts/audiobook/loop_decisions.jsonl")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": trace.timestamp_utc,
            "run_id": trace.run_id,
            "section_id": trace.section_id,
            "locale": trace.locale,
            "loop_index": trace.loop_index,
            "decision": trace.final_decision,
            "aggregate_score": trace.aggregate_score,
            "hard_gates_passed": trace.hard_gates_passed,
        }, ensure_ascii=False) + "\n")


def _write_manual_review_packet(repo: Path, cfg: dict, result: SectionResult) -> None:
    """
    Write the full manual review packet for a section that exhausted max_loops.
    Contents: best_draft.txt, final_draft.txt, defect_history.json,
              review_summary.txt, status.json.
    Appends entry to manual_review_queue.json (high-visibility; PhoenixControl UI reads this).
    """
    artifact_cfg = cfg.get("artifact_trace", {})
    packet_dir = (
        repo
        / artifact_cfg.get("base_path", "artifacts/audiobook")
        / result.batch_id / result.book_id / result.section_id / "manual_review"
    )
    packet_dir.mkdir(parents=True, exist_ok=True)

    # best_draft.txt — highest aggregate_score draft
    (packet_dir / "best_draft.txt").write_text(result.best_draft, encoding="utf-8")

    # final_draft.txt — last loop draft (may differ from best)
    (packet_dir / "final_draft.txt").write_text(result.final_draft, encoding="utf-8")

    # defect_history.json — all gate_results across all loops
    defect_history = [
        {"loop_index": t.loop_index, "gate_results": t.gate_results, "aggregate_score": t.aggregate_score}
        for t in result.loop_traces
    ]
    (packet_dir / "defect_history.json").write_text(
        json.dumps(defect_history, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # review_summary.txt — human-readable review brief
    summary_lines = [
        f"MANUAL REVIEW REQUIRED",
        f"=====================",
        f"section_id:    {result.section_id}",
        f"locale:        {result.locale}",
        f"book_id:       {result.book_id}",
        f"batch_id:      {result.batch_id}",
        f"loops_attempted: {result.loops_attempted}",
        f"best_aggregate_score: {result.best_aggregate_score:.3f} (loop {result.best_loop_index})",
        f"",
        f"Loop-by-loop summary:",
    ]
    for t in result.loop_traces:
        failed_gates = [g["gate_id"] for g in t.gate_results if not g.get("pass", True)]
        summary_lines.append(
            f"  Loop {t.loop_index}: score={t.aggregate_score:.3f}, "
            f"hard_passed={t.hard_gates_passed}, "
            f"failed_gates={failed_gates or 'none'}"
        )
    summary_lines += [
        f"",
        f"Recommended fix direction:",
        f"  See defect_history.json for gate-level defects and prompt_patch suggestions.",
        f"  best_draft.txt = highest-scoring draft across all loops.",
        f"  final_draft.txt = last loop draft.",
        f"  Fix the issues in best_draft.txt and re-run the section if needed.",
    ]
    (packet_dir / "review_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    # status.json
    hard_fail_count = sum(
        1 for t in result.loop_traces
        for g in t.gate_results
        if not g.get("pass", True) and (g.get("gate_type") == "hard")
    )
    status = {
        "requires_manual_review": True,
        "section_id": result.section_id,
        "locale": result.locale,
        "book_id": result.book_id,
        "batch_id": result.batch_id,
        "hard_gate_failures": hard_fail_count,
        "best_aggregate_score": result.best_aggregate_score,
        "loops_attempted": result.loops_attempted,
        "packet_path": str(packet_dir),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (packet_dir / "status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to global manual_review_queue.json (high-visibility; PhoenixControl UI)
    queue_path = repo / artifact_cfg.get(
        "manual_review_queue_file", "artifacts/audiobook/manual_review_queue.json"
    )
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue: list[dict] = []
    if queue_path.exists():
        try:
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
        except Exception:
            queue = []
    # Avoid duplicates: remove any existing entry for same section+locale+batch
    queue = [
        e for e in queue
        if not (e.get("section_id") == result.section_id
                and e.get("locale") == result.locale
                and e.get("batch_id") == result.batch_id)
    ]
    queue.append({
        "section_id": result.section_id,
        "locale": result.locale,
        "book_id": result.book_id,
        "batch_id": result.batch_id,
        "hard_gate_failures": hard_fail_count,
        "aggregate_score_best": result.best_aggregate_score,
        "loops_attempted": result.loops_attempted,
        "packet_path": str(packet_dir),
        "timestamp_utc": status["timestamp_utc"],
    })
    # Sort by severity: most hard gate failures first
    queue.sort(key=lambda e: -e.get("hard_gate_failures", 0))
    queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.warning(
        "MANUAL REVIEW REQUIRED: section=%s locale=%s batch=%s → %s",
        result.section_id, result.locale, result.batch_id, packet_dir
    )

# ─── SECTION-LEVEL LOOP ──────────────────────────────────────────────────────

async def run_section_loop(
    section_id: str,
    locale: str,
    book_id: str,
    batch_id: str,
    english_source: str,
    cfg: dict,
    checklist: dict,
    result_schema: dict,
    base_system_prompt: str,
    judge_system_prompt: str,
    repo: Path,
    semaphore: asyncio.Semaphore,
) -> SectionResult:
    """
    Run the comparator loop for one section. Fully automated — no human in loop.
    Semaphore limits concurrent section workers.
    """
    async with semaphore:
        loop_cfg = cfg.get("loop_control", {})
        max_loops = loop_cfg.get("max_loops", 3)
        patch_applier = PatchApplier(cfg, checklist)

        loop_traces: list[LoopTrace] = []
        current_system_prompt = base_system_prompt
        best_draft = ""
        final_draft = ""
        best_score = -1.0
        best_loop_index = 1

        run_id = f"{batch_id}__{book_id}__{section_id}__{locale}"
        draft_seed = _section_seed(section_id, locale)

        for loop_index in range(1, max_loops + 1):
            ts = datetime.now(timezone.utc).isoformat()
            logger.info("Loop %d/%d: section=%s locale=%s", loop_index, max_loops, section_id, locale)

            # 1. Generate Qwen draft
            try:
                draft_text = await asyncio.wait_for(
                    _call_qwen_draft(english_source, locale, current_system_prompt, cfg, seed=draft_seed),
                    timeout=cfg.get("draft_model", {}).get("timeout_seconds", 60),
                )
            except asyncio.TimeoutError:
                logger.error("Draft timeout: section=%s loop=%d", section_id, loop_index)
                break
            except NotImplementedError:
                raise   # propagate NotImplementedError so tests can stub it
            except Exception as e:
                logger.error("Draft failed: section=%s loop=%d error=%s", section_id, loop_index, e)
                break

            input_draft_hash = _sha256(draft_text)
            final_draft = draft_text

            # 2. Call judge
            judge_seed = _judge_seed(section_id, loop_index)
            try:
                judge_raw = await asyncio.wait_for(
                    _call_qwen_judge(english_source, draft_text, locale, judge_system_prompt, cfg, seed=judge_seed),
                    timeout=cfg.get("judge_model", {}).get("timeout_seconds", 45),
                )
            except asyncio.TimeoutError:
                logger.error("Judge timeout: section=%s loop=%d → manual_review", section_id, loop_index)
                decision = "manual_review"
                trace = LoopTrace(
                    run_id=run_id, batch_id=batch_id, book_id=book_id,
                    section_id=section_id, locale=locale, loop_index=loop_index,
                    input_draft_hash=input_draft_hash, prompt_patch="",
                    rerun_prompt_hash="", aggregate_score=0.0,
                    hard_gates_passed=False, final_decision=decision,
                    timestamp_utc=ts, gate_results=[],
                )
                loop_traces.append(trace)
                _write_loop_trace(repo, cfg, trace)
                break
            except NotImplementedError:
                raise
            except Exception as e:
                logger.error("Judge failed: section=%s loop=%d error=%s → manual_review", section_id, loop_index, e)
                break

            # 3. Validate judge JSON output (schema + version binding)
            checklist_version = checklist.get("schema_version", "2.0")
            valid, gate_results, schema_err = _validate_judge_output(judge_raw, result_schema, checklist_version)
            if not valid:
                logger.error(
                    "Judge schema fail: section=%s loop=%d err=%s → manual_review",
                    section_id, loop_index, schema_err
                )
                decision = "manual_review"
                trace = LoopTrace(
                    run_id=run_id, batch_id=batch_id, book_id=book_id,
                    section_id=section_id, locale=locale, loop_index=loop_index,
                    input_draft_hash=input_draft_hash, prompt_patch="",
                    rerun_prompt_hash="", aggregate_score=0.0,
                    hard_gates_passed=False, final_decision=decision,
                    timestamp_utc=ts,
                    gate_results=[{"schema_error": schema_err}],
                )
                loop_traces.append(trace)
                _write_loop_trace(repo, cfg, trace)
                # Never silent pass on schema fail
                break

            # 4. Score aggregation
            aggregate_score, all_hard_passed = _aggregate_score(gate_results or [], checklist)

            # Track best-scoring draft
            if aggregate_score > best_score:
                best_score = aggregate_score
                best_draft = draft_text
                best_loop_index = loop_index

            # 5. Determine decision
            if _passes_threshold(aggregate_score, all_hard_passed, cfg, locale):
                decision = "pass"
            elif loop_index < max_loops:
                decision = "continue"
            else:
                decision = "manual_review"

            # 6. Assemble patch for next loop (empty on pass or final loop)
            patch_block = ""
            next_prompt_hash = ""
            if decision == "continue" and gate_results:
                next_system_prompt = patch_applier.assemble(current_system_prompt, gate_results, loop_index + 1)
                next_prompt_hash = _sha256(next_system_prompt)
                patch_block = next_system_prompt[len(current_system_prompt):]  # just the appended block
                current_system_prompt = next_system_prompt

            # 7. Write trace
            trace = LoopTrace(
                run_id=run_id, batch_id=batch_id, book_id=book_id,
                section_id=section_id, locale=locale, loop_index=loop_index,
                input_draft_hash=input_draft_hash,
                prompt_patch=patch_block,
                rerun_prompt_hash=next_prompt_hash,
                aggregate_score=aggregate_score,
                hard_gates_passed=all_hard_passed,
                final_decision=decision,
                timestamp_utc=ts,
                gate_results=gate_results or [],
            )
            loop_traces.append(trace)
            _write_loop_trace(repo, cfg, trace)

            if decision != "continue":
                break

        # 8. Final result
        final_decision = loop_traces[-1].final_decision if loop_traces else "manual_review"
        section_result = SectionResult(
            section_id=section_id,
            locale=locale,
            book_id=book_id,
            batch_id=batch_id,
            decision=final_decision,
            loops_attempted=len(loop_traces),
            best_loop_index=best_loop_index,
            best_aggregate_score=best_score,
            best_draft=best_draft,
            final_draft=final_draft,
            loop_traces=loop_traces,
        )

        if final_decision == "manual_review":
            _write_manual_review_packet(repo, cfg, section_result)

        return section_result

# ─── BOOK-LEVEL PARALLEL RUNNER ───────────────────────────────────────────────

async def run_book_parallel(
    book_id: str,
    batch_id: str,
    locale: str,
    sections: list[dict],   # [{section_id, english_source_text}]
    cfg: dict,
    checklist: dict,
    result_schema: dict,
    base_system_prompt: str,
    judge_system_prompt: str,
    repo: Path,
) -> list[SectionResult]:
    """
    Process all sections of a book in parallel, bounded by max_parallel_sections.
    Each section runs its own comparator loop independently.
    Returns list of SectionResult (one per section).
    """
    parallel_cfg = cfg.get("parallel", {})
    max_workers = parallel_cfg.get("max_parallel_sections", 6)
    semaphore = asyncio.Semaphore(max_workers)
    book_timeout = parallel_cfg.get("batch_timeout_seconds", 7200)

    tasks = [
        run_section_loop(
            section_id=s["section_id"],
            locale=locale,
            book_id=book_id,
            batch_id=batch_id,
            english_source=s["english_source_text"],
            cfg=cfg,
            checklist=checklist,
            result_schema=result_schema,
            base_system_prompt=base_system_prompt,
            judge_system_prompt=judge_system_prompt,
            repo=repo,
            semaphore=semaphore,
        )
        for s in sections
    ]

    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=book_timeout)
    except asyncio.TimeoutError:
        logger.error("Book-level timeout: book=%s batch=%s", book_id, batch_id)
        results = []

    processed: list[SectionResult] = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            section_id = sections[i]["section_id"] if i < len(sections) else f"section_{i}"
            logger.error("Section %s failed with exception: %s", section_id, r)
            processed.append(SectionResult(
                section_id=section_id, locale=locale, book_id=book_id, batch_id=batch_id,
                decision="manual_review", loops_attempted=0, best_loop_index=0,
                best_aggregate_score=0.0, best_draft="", final_draft="",
                error=str(r),
            ))
        else:
            processed.append(r)
    return processed


# ─── BATCH SUMMARY ────────────────────────────────────────────────────────────

def _write_batch_summary(repo: Path, cfg: dict, batch_id: str, results: list[SectionResult]) -> None:
    artifact_cfg = cfg.get("artifact_trace", {})
    summary_path_template = artifact_cfg.get("batch_summary_file", "artifacts/audiobook/{batch_id}/batch_summary.json")
    summary_path = repo / summary_path_template.format(batch_id=batch_id)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    passed = [r for r in results if r.decision == "pass"]
    manual = [r for r in results if r.decision == "manual_review"]
    summary = {
        "batch_id": batch_id,
        "total_sections": len(results),
        "passed": len(passed),
        "manual_review": len(manual),
        "pass_rate": round(len(passed) / len(results), 4) if results else 0.0,
        "manual_review_rate": round(len(manual) / len(results), 4) if results else 0.0,
        "sections": [
            {
                "section_id": r.section_id,
                "locale": r.locale,
                "book_id": r.book_id,
                "decision": r.decision,
                "loops_attempted": r.loops_attempted,
                "best_aggregate_score": r.best_aggregate_score,
            }
            for r in results
        ],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Batch summary: %s (pass=%d manual=%d)", batch_id, len(passed), len(manual))

    # Observability alerts
    obs_cfg = cfg.get("observability", {})
    mr_alert_threshold = obs_cfg.get("alert_on_manual_review_rate_above", 0.10)
    if summary["manual_review_rate"] > mr_alert_threshold:
        logger.warning(
            "ALERT: manual_review_rate=%.2f exceeds threshold %.2f for batch=%s",
            summary["manual_review_rate"], mr_alert_threshold, batch_id
        )

# ─── PROMPT LOADING STUB ──────────────────────────────────────────────────────

def _load_prompt(repo: Path, prompt_id: str) -> str:
    """Load prompt from prompts/ directory. Stub — implement per deployment."""
    prompt_path = repo / "prompts" / f"{prompt_id}.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    logger.warning("Prompt file not found: %s — using empty stub", prompt_path)
    return f"[STUB: implement prompt {prompt_id}]"

# ─── CLI ENTRYPOINT ───────────────────────────────────────────────────────────

def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    ap = argparse.ArgumentParser(
        description="Qwen-Only Audiobook Comparator Loop — parallel, fully automated, no human in loop."
    )
    ap.add_argument("--section-id", help="Single section ID (debug/test mode)")
    ap.add_argument("--locale", required=True, help="Target locale (e.g. zh-TW, ja-JP)")
    ap.add_argument("--book-id", help="Book ID")
    ap.add_argument("--batch-id", required=True, help="Batch run ID (used in artifact paths)")
    ap.add_argument("--english-source", help="Path to English source text file (single section mode)")
    ap.add_argument(
        "--sections-manifest",
        help="Path to JSON manifest [{section_id, english_source_text}] for full book mode"
    )
    ap.add_argument(
        "--batch-manifest",
        help="Path to JSON manifest [{book_id, locale, sections_manifest_path}] for full batch mode"
    )
    ap.add_argument("--regression-run", action="store_true", help="Run against golden regression set")
    ap.add_argument("--golden-set", help="Path to golden regression set directory")
    ap.add_argument("--repo", default=None, help="Repo root (default: script grandparent)")
    ap.add_argument("--dry-run", action="store_true", help="Validate config/schema only; no API calls")
    args = ap.parse_args()

    repo = Path(args.repo) if args.repo else REPO_ROOT
    cfg = _load_config(repo)
    checklist = _load_checklist(repo)
    result_schema = _load_result_schema(repo)

    if args.dry_run:
        print("Dry run: config, checklist, and schema loaded successfully.")
        print(f"  max_loops={cfg['loop_control']['max_loops']} (schema-validated range [1,5])")
        print(f"  max_parallel_sections={cfg['parallel']['max_parallel_sections']}")
        print(f"  min_scored_pass_threshold={cfg['scoring']['min_scored_pass_threshold']}")
        print(f"  judge_model={cfg['judge_model']['model_id']} temp={cfg['judge_model']['temperature']}")
        print(f"  gates={[g['gate_id'] for g in checklist.get('gates', [])]}")
        return 0

    draft_prompt = _load_prompt(repo, cfg["draft_model"]["system_prompt_id"])
    judge_prompt = _load_prompt(repo, cfg["judge_model"]["system_prompt_id"])

    if args.section_id and args.english_source:
        # Single section mode
        english_source = Path(args.english_source).read_text(encoding="utf-8")
        result = asyncio.run(run_section_loop(
            section_id=args.section_id,
            locale=args.locale,
            book_id=args.book_id or "unknown",
            batch_id=args.batch_id,
            english_source=english_source,
            cfg=cfg,
            checklist=checklist,
            result_schema=result_schema,
            base_system_prompt=draft_prompt,
            judge_system_prompt=judge_prompt,
            repo=repo,
            semaphore=asyncio.Semaphore(1),
        ))
        print(f"Section {result.section_id}: {result.decision} "
              f"(loops={result.loops_attempted}, score={result.best_aggregate_score:.3f})")
        return 0 if result.decision == "pass" else 1

    if args.sections_manifest:
        # Full book mode
        sections = json.loads(Path(args.sections_manifest).read_text(encoding="utf-8"))
        results = asyncio.run(run_book_parallel(
            book_id=args.book_id or "unknown",
            batch_id=args.batch_id,
            locale=args.locale,
            sections=sections,
            cfg=cfg,
            checklist=checklist,
            result_schema=result_schema,
            base_system_prompt=draft_prompt,
            judge_system_prompt=judge_prompt,
            repo=repo,
        ))
        _write_batch_summary(repo, cfg, args.batch_id, results)
        manual = [r for r in results if r.decision == "manual_review"]
        print(f"Book complete: {len(results)} sections, {len(manual)} manual_review")
        return 1 if manual else 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
