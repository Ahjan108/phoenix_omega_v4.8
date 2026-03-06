#!/usr/bin/env python3
"""
AI/LLM cohesive bestseller tester: robust, intelligent testing of 10k Pearl Prime CLI
books + 10k teacher-mode (all personas × topics) + v2 EI to determine what is 100%.

Features:
- Reads all config: canonical personas, topics, teacher matrix, format registry, EI v2.
- Validates simulation JSON and LLM responses; graceful degradation on missing inputs.
- Dimension-aware analysis: pass rate by format/tier, phase2/phase3 breakdown, EI v2
  10-dimension thresholds (therapeutic_value, emotional_coherence, engagement, etc.).
- Coverage intelligence: persona/topic/format coverage from sim; teacher matrix coverage.
- Severity levels: CRITICAL (bestseller fail), HIGH (tier A / phase2/3 fail), MEDIUM/LOW.
- Health score 0–100; optional baseline comparison for regression.
- LLM with retry and structured output validation; richer prompt with quality rubrics.

Usage:
  python scripts/ci/llm_cohesive_bestseller_tester.py --read-all
  python scripts/ci/llm_cohesive_bestseller_tester.py -i artifacts/simulation_10k.json \\
    --teacher-matrix --ei-v2-report --llm --baseline artifacts/reports/cohesive_baseline.json
  python scripts/ci/llm_cohesive_bestseller_tester.py --run-pearl-10k --teacher-matrix --llm --require-100
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Format IDs / names that are "bestseller" tier (template/premium)
BESTSELLER_PREFIX = "bestseller"
TIER_A = "A"

# EI v2 quality dimension keys and minimum acceptable score (below = flag)
EI_V2_DIMENSIONS = (
    "therapeutic_value", "emotional_coherence", "engagement", "chapter_journey",
    "cohesion", "listen_experience", "marketability", "safety_compliance",
    "content_uniqueness", "somatic_precision",
)
EI_V2_DIMENSION_THRESHOLD = 0.5  # below this = dimension_fail
HEALTH_WEIGHT_PEARL_PASS = 0.4
HEALTH_WEIGHT_BESTSELLER_OK = 0.3
HEALTH_WEIGHT_EI_V2 = 0.2
HEALTH_WEIGHT_COVERAGE = 0.1


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        if path.exists():
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    return {}


def read_all_config() -> dict:
    """Test read all: canonical personas, topics, teacher matrix, format registry, EI v2."""
    config_dir = REPO_ROOT / "config"
    catalog = config_dir / "catalog_planning"
    format_sel = config_dir / "format_selection"
    quality_cfg = config_dir / "quality" / "ei_v2_config.yaml"

    personas_path = catalog / "canonical_personas.yaml"
    topics_path = catalog / "canonical_topics.yaml"
    teacher_matrix_path = catalog / "teacher_persona_matrix.yaml"
    format_registry_path = format_sel / "format_registry.yaml"

    personas_data = _load_yaml(personas_path)
    topics_data = _load_yaml(topics_path)
    teacher_data = _load_yaml(teacher_matrix_path)
    format_data = _load_yaml(format_registry_path)

    personas = (personas_data or {}).get("personas", [])
    topics = (topics_data or {}).get("topics", [])
    teachers_map = (teacher_data or {}).get("teachers", {})
    structural = (format_data or {}).get("structural_formats", {})
    runtime = (format_data or {}).get("runtime_formats", {})

    teacher_summary = {}
    for tid, t in teachers_map.items():
        teacher_summary[tid] = {
            "allowed_personas": len(t.get("allowed_personas", [])),
            "allowed_engines": list(t.get("allowed_engines", [])),
        }

    ei_v2_summary = {}
    if quality_cfg.exists():
        ei_v2_data = _load_yaml(quality_cfg)
        for k, v in (ei_v2_data or {}).items():
            if isinstance(v, dict) and "enabled" in v:
                ei_v2_summary[k] = {"enabled": v.get("enabled")}

    return {
        "canonical_personas": personas,
        "canonical_topics": topics,
        "personas_count": len(personas),
        "topics_count": len(topics),
        "teachers": list(teachers_map.keys()),
        "teachers_count": len(teachers_map),
        "teacher_summary": teacher_summary,
        "structural_formats": list(structural.keys()),
        "runtime_formats": list(runtime.keys()),
        "ei_v2_config_path": str(quality_cfg),
        "ei_v2_enabled_modules": ei_v2_summary,
    }


def build_teacher_mode_matrix(config: dict, cap: int = 10_000) -> list[dict]:
    """Build teacher-mode test matrix: (teacher_id, persona_id, topic_id, engine) up to cap."""
    teachers_map = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml")
    teachers_map = (teachers_map or {}).get("teachers", {})
    personas = config.get("canonical_personas", [])
    topics = config.get("canonical_topics", [])

    matrix = []
    for teacher_id, t in teachers_map.items():
        allowed_personas = t.get("allowed_personas", [])
        allowed_engines = t.get("allowed_engines", [])
        for persona_id in allowed_personas:
            if persona_id not in personas:
                continue
            for topic_id in topics:
                for engine in allowed_engines:
                    matrix.append({
                        "teacher_id": teacher_id,
                        "persona_id": persona_id,
                        "topic_id": topic_id,
                        "engine": engine,
                    })
                    if len(matrix) >= cap:
                        return matrix
    return matrix


def validate_sim_structure(data: dict) -> tuple[bool, list[str]]:
    """Validate simulation JSON has expected structure. Returns (ok, errors)."""
    errs: list[str] = []
    if not isinstance(data, dict):
        return False, ["Root is not a dict"]
    if "results" not in data:
        errs.append("Missing 'results' key")
    else:
        r = data["results"]
        if not isinstance(r, list):
            errs.append("'results' is not a list")
        elif r and not isinstance(r[0], dict):
            errs.append("'results' items are not dicts")
        elif r and "passed" not in r[0] and "format_id" not in r[0]:
            errs.append("Result items missing 'passed' or 'format_id'")
    return len(errs) == 0, errs


def load_pearl_prime_sim(path: Path) -> tuple[list[dict], dict, list[str]]:
    """Load and validate Pearl Prime simulation JSON. Returns (results, summary, validation_errors)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return [], {}, [f"Could not read file: {e}"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return [], {}, [f"Invalid JSON: {e}"]
    ok, errs = validate_sim_structure(data)
    if not ok:
        return data.get("results", []), data.get("summary", {}), errs
    return data.get("results", []), data.get("summary", {}), []


def load_ei_v2_report(path: Path | None = None) -> dict | None:
    """Load EI v2 rigorous eval report if present."""
    p = path or REPO_ROOT / "artifacts" / "ei_v2" / "eval_rigorous_report.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def analyze_pearl_dimensions(results: list[dict], summary: dict) -> dict:
    """Intelligent analysis: pass rate by format/tier, phase2/3 breakdown, worst combos."""
    n = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    by_format: dict[str, dict] = {}
    by_tier: dict[str, dict] = {}
    phase2_fail = sum(1 for r in results if r.get("phase2_passed") is False)
    phase3_fail = sum(1 for r in results if r.get("phase3_passed") is False)
    for r in results:
        fid = r.get("format_id", "?")
        tier = r.get("tier", "?")
        ok = r.get("passed", False)
        by_format.setdefault(fid, {"pass": 0, "fail": 0, "total": 0})
        by_format[fid]["total"] += 1
        if ok:
            by_format[fid]["pass"] += 1
        else:
            by_format[fid]["fail"] += 1
        by_tier.setdefault(tier, {"pass": 0, "fail": 0, "total": 0})
        by_tier[tier]["total"] += 1
        if ok:
            by_tier[tier]["pass"] += 1
        else:
            by_tier[tier]["fail"] += 1
    pass_rate_fmt = {f: d["pass"] / d["total"] if d["total"] else 0 for f, d in by_format.items()}
    pass_rate_tier = {t: d["pass"] / d["total"] if d["total"] else 0 for t, d in by_tier.items()}
    worst_formats = sorted(pass_rate_fmt.items(), key=lambda x: x[1])[:5]
    worst_tiers = sorted(pass_rate_tier.items(), key=lambda x: x[1])[:3]
    return {
        "n": n,
        "passed": passed,
        "overall_pass_rate": passed / n if n else 0,
        "pass_rate_by_format": pass_rate_fmt,
        "pass_rate_by_tier": pass_rate_tier,
        "phase2_failed_count": phase2_fail,
        "phase3_failed_count": phase3_fail,
        "worst_formats": [{"format_id": f, "pass_rate": r} for f, r in worst_formats],
        "worst_tiers": [{"tier": t, "pass_rate": r} for t, r in worst_tiers],
        "summary_phase2": summary.get("phase2", {}),
        "summary_phase3": summary.get("phase3", {}),
    }


def coverage_from_pearl_results(results: list[dict]) -> dict:
    """Extract persona/topic/format coverage from sim results (request_id or keys)."""
    personas: set[str] = set()
    topics: set[str] = set()
    formats: set[str] = set()
    for r in results:
        fid = r.get("format_id") or r.get("tier")
        if fid:
            formats.add(str(fid))
        rid = r.get("request_id") or ""
        for part in rid.replace("_", " ").split():
            if part in ("bk", "book", "standard", "short", "deep", "micro"):
                continue
            if len(part) > 3:
                personas.add(part)
                topics.add(part)
    return {
        "formats_seen": sorted(formats),
        "formats_count": len(formats),
        "personas_mentioned": sorted(personas)[:20],
        "topics_mentioned": sorted(topics)[:20],
    }


def classify_severity(pearl_identified: dict | None, pearl_dims: dict | None) -> dict:
    """Classify issues into CRITICAL / HIGH / MEDIUM / LOW."""
    issues: dict[str, list[dict]] = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
    if pearl_identified:
        if pearl_identified.get("bestseller_failed", 0) > 0:
            issues["CRITICAL"].append({
                "kind": "bestseller_failure",
                "count": pearl_identified["bestseller_failed"],
                "message": "Bestseller-tier or Tier A books failed",
            })
        if pearl_identified.get("total_failed", 0) > 0:
            issues["HIGH"].append({
                "kind": "pearl_failure",
                "count": pearl_identified["total_failed"],
                "message": f"Phase 1 failures: {pearl_identified['total_failed']}",
            })
    if pearl_dims:
        if pearl_dims.get("phase2_failed_count", 0) > 0:
            issues["HIGH"].append({
                "kind": "phase2_failure",
                "count": pearl_dims["phase2_failed_count"],
                "message": "Phase 2 (waveform/arc/drift) failures",
            })
        if pearl_dims.get("phase3_failed_count", 0) > 0:
            issues["HIGH"].append({
                "kind": "phase3_failure",
                "count": pearl_dims["phase3_failed_count"],
                "message": "Phase 3 (content/emotional) failures",
            })
        rate = pearl_dims.get("overall_pass_rate", 0)
        if rate < 0.95 and rate > 0:
            issues["MEDIUM"].append({
                "kind": "pass_rate_below_95",
                "rate": rate,
                "message": f"Overall pass rate {rate:.1%} < 95%",
            })
    return issues


def analyze_ei_v2_dimensions(report: dict | None, threshold: float = EI_V2_DIMENSION_THRESHOLD) -> dict | None:
    """Check EI v2 quality dimensions against threshold; return dimension_fails and score summary."""
    if not report:
        return None
    quality = report.get("quality_scores", {})
    if not quality:
        return None
    dimension_fails: list[dict] = []
    for dim in EI_V2_DIMENSIONS:
        score = quality.get(dim)
        if score is not None and isinstance(score, (int, float)) and score < threshold:
            dimension_fails.append({"dimension": dim, "score": score, "threshold": threshold})
    overall = quality.get("overall_composite")
    return {
        "dimension_fails": dimension_fails,
        "overall_composite": overall,
        "threshold_used": threshold,
        "all_scores": {k: quality.get(k) for k in EI_V2_DIMENSIONS if quality.get(k) is not None},
    }


def compute_health_score(
    pearl_identified: dict | None,
    pearl_dims: dict | None,
    ei_v2_dims: dict | None,
    teacher_matrix_size: int,
    config: dict,
) -> float:
    """Compute 0–100 health score from pass rates, bestseller ok, EI v2, coverage."""
    score = 0.0
    if pearl_identified and pearl_identified.get("total", 0) > 0:
        rate = pearl_identified["total_passed"] / pearl_identified["total"]
        score += HEALTH_WEIGHT_PEARL_PASS * (rate * 100)
        if pearl_identified.get("bestseller_failed", 0) == 0:
            score += HEALTH_WEIGHT_BESTSELLER_OK * 100
        else:
            score += HEALTH_WEIGHT_BESTSELLER_OK * max(0, 100 - pearl_identified["bestseller_failed"] * 2)
    else:
        score += (HEALTH_WEIGHT_PEARL_PASS + HEALTH_WEIGHT_BESTSELLER_OK) * 50  # neutral
    if ei_v2_dims:
        comp = ei_v2_dims.get("overall_composite")
        if comp is not None:
            score += HEALTH_WEIGHT_EI_V2 * (comp * 100)
        dim_fails = len(ei_v2_dims.get("dimension_fails", []))
        if dim_fails > 0:
            score -= min(20, dim_fails * 5)
    else:
        score += HEALTH_WEIGHT_EI_V2 * 50
    expected_slots = (config.get("personas_count", 0) or 1) * (config.get("topics_count", 0) or 1) * max(1, config.get("teachers_count", 0)) * 5
    if expected_slots > 0 and teacher_matrix_size > 0:
        coverage_ratio = min(1.0, teacher_matrix_size / min(expected_slots, 10_000))
        score += HEALTH_WEIGHT_COVERAGE * (coverage_ratio * 100)
    else:
        score += HEALTH_WEIGHT_COVERAGE * 50
    return max(0.0, min(100.0, round(score, 1)))


def identify_bestseller_errors(results: list[dict]) -> dict:
    """From Pearl Prime results, tag failures on bestseller-tier formats and all failures."""
    failed = [r for r in results if not r.get("passed")]
    bestseller_failures = [
        r for r in failed
        if (BESTSELLER_PREFIX in (r.get("format_id") or "").lower())
        or (r.get("tier") == TIER_A)
    ]
    return {
        "total_failed": len(failed),
        "total_passed": sum(1 for r in results if r.get("passed")),
        "total": len(results),
        "bestseller_failed": len(bestseller_failures),
        "bestseller_errors": [
            {
                "request_id": r.get("request_id"),
                "format_id": r.get("format_id"),
                "tier": r.get("tier"),
                "errors": r.get("errors", []),
                "phase2_errors": r.get("phase2_errors", []),
                "phase3_errors": r.get("phase3_errors", []),
            }
            for r in bestseller_failures[:50]
        ],
        "all_failure_sample": [
            {
                "request_id": r.get("request_id"),
                "format_id": r.get("format_id"),
                "tier": r.get("tier"),
                "errors": (r.get("errors") or [])[:5],
            }
            for r in failed[:30]
        ],
        "error_reasons_summary": _count_error_reasons(failed),
    }


def _count_error_reasons(failed: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in failed:
        for e in r.get("errors") or []:
            out[e] = out.get(e, 0) + 1
    return dict(sorted(out.items(), key=lambda x: -x[1]))


def build_llm_prompt(
    config: dict,
    pearl_identified: dict | None,
    pearl_dims: dict | None,
    teacher_matrix: list[dict],
    ei_v2_report: dict | None,
    ei_v2_dims: dict | None,
    severity: dict,
    health_score: float,
) -> str:
    """Build prompt for LLM with quality rubrics and severity context."""
    lines = [
        "## Cohesive Bestseller Tester — Robust Analysis",
        "Quality dimensions (EI v2): therapeutic_value, emotional_coherence, engagement, chapter_journey, cohesion, listen_experience, marketability, safety_compliance, content_uniqueness, somatic_precision. Bestseller tier requires high scores on all.",
        "",
        "Config:",
        f"  Personas: {config.get('personas_count', 0)}  Topics: {config.get('topics_count', 0)}  Teachers: {config.get('teachers_count', 0)}",
        f"  Health score (0–100): {health_score}",
        "",
        "Severity summary:",
        json.dumps(severity, indent=2),
        "",
    ]

    if pearl_identified:
        lines.extend([
            "## Pearl Prime 10k",
            f"Total: {pearl_identified.get('total', 0)}  Passed: {pearl_identified.get('total_passed', 0)}  Failed: {pearl_identified.get('total_failed', 0)}  Bestseller failures: {pearl_identified.get('bestseller_failed', 0)}",
            "Error reason counts: " + json.dumps(pearl_identified.get("error_reasons_summary", {}), ensure_ascii=False),
            "Bestseller failures (sample): " + json.dumps(pearl_identified.get("bestseller_errors", [])[:15], ensure_ascii=False),
            "",
        ])
    if pearl_dims:
        lines.extend([
            "Pearl dimension analysis:",
            f"  Overall pass rate: {pearl_dims.get('overall_pass_rate', 0):.2%}  Phase2 failed: {pearl_dims.get('phase2_failed_count', 0)}  Phase3 failed: {pearl_dims.get('phase3_failed_count', 0)}",
            f"  Worst formats: {pearl_dims.get('worst_formats', [])}",
            "",
        ])

    lines.append(f"## Teacher-mode matrix: {len(teacher_matrix)} slots (personas × topics × teachers × engines)")

    if ei_v2_report:
        quality = ei_v2_report.get("quality_scores", {})
        v1v2 = ei_v2_report.get("v1_vs_v2", {})
        lines.extend([
            "",
            "## EI v2",
            f"Overall composite: {quality.get('overall_composite')}  V1V2 agreement: {v1v2.get('agreement_rate')}  safety/dedup/TTS/arc flags: {v1v2.get('safety_flags')}/{v1v2.get('dedup_flags')}/{v1v2.get('tts_issues')}/{v1v2.get('arc_issues')}",
        ])
    if ei_v2_dims and ei_v2_dims.get("dimension_fails"):
        lines.append(f"Dimensions below threshold: {[d['dimension'] for d in ei_v2_dims['dimension_fails']]}")
    lines.append("")

    lines.extend([
        "Tasks: (1) What is 100%: which segments/dimensions are fully passing. (2) Bestseller gaps: failures or gaps that prevent bestseller quality. (3) Root causes and one-line recommendations.",
        'Reply with valid JSON only: {"what_is_100_percent": ["..."], "bestseller_gaps": [{"summary": "...", "segment": "pearl|teacher|ei_v2"}], "root_causes": [{"category": "...", "recommendation": "..."}]}',
    ])
    return "\n".join(lines)


def validate_llm_response(obj: dict) -> tuple[bool, list[str]]:
    """Ensure LLM response has expected keys. Returns (valid, list of missing keys)."""
    required = ["what_is_100_percent", "bestseller_gaps", "root_causes"]
    missing = [k for k in required if k not in obj or not isinstance(obj.get(k), list)]
    return len(missing) == 0, missing


def _parse_llm_json(text: str) -> dict | None:
    """Extract and parse JSON from LLM text (handles markdown code blocks)."""
    if "```" in text:
        for part in text.split("```"):
            s = part.strip()
            if s.startswith("json"):
                s = s[4:].strip()
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def call_llm(prompt: str, dry_run: bool, max_retries: int = 2) -> dict:
    """Call LLM with retry and response validation."""
    if dry_run:
        return {"llm_skipped": True, "reason": "dry_run"}
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"llm_skipped": True, "reason": "no_api_key"}
    try:
        import anthropic
    except ImportError:
        return {"llm_skipped": True, "reason": "anthropic_not_installed"}
    last_error: str | None = None
    for attempt in range(max_retries + 1):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system="You are a QA analyst for self-help audiobook pipelines. Reply only with valid JSON; no markdown or commentary.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            if msg.content and isinstance(msg.content, list) and len(msg.content) > 0:
                block = msg.content[0]
                text = block.text if hasattr(block, "text") else (block.get("text", "") if isinstance(block, dict) else "")
                if text:
                    parsed = _parse_llm_json(text)
                    if parsed and isinstance(parsed, dict):
                        valid, missing = validate_llm_response(parsed)
                        if valid:
                            return parsed
                        if attempt < max_retries:
                            time.sleep(1.5)
                            continue
                        return {**parsed, "llm_validation_warning": f"missing_keys: {missing}"}
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                time.sleep(2.0)
                continue
            return {"llm_skipped": True, "reason": "llm_error", "error": last_error}
    return {"llm_skipped": True, "reason": "no_response", "error": last_error}


def load_baseline(path: Path) -> dict | None:
    """Load baseline JSON for regression comparison."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def compare_to_baseline(report: dict, baseline: dict | None) -> dict | None:
    """Compare current health and pass rates to baseline; return diff or None."""
    if not baseline:
        return None
    out: dict = {"health_score_regression": None, "pearl_pass_rate_regression": None, "warnings": []}
    cur_health = report.get("health_score")
    base_health = baseline.get("health_score")
    if cur_health is not None and base_health is not None:
        delta = cur_health - base_health
        out["health_score_regression"] = {"current": cur_health, "baseline": base_health, "delta": round(delta, 1)}
        if delta < -5:
            out["warnings"].append(f"Health score dropped by {abs(delta):.1f} vs baseline")
    pp = report.get("pearl_prime_10k")
    bp = baseline.get("pearl_prime_10k")
    if pp and bp and pp.get("total") and bp.get("total"):
        cur_rate = pp["passed"] / pp["total"]
        base_rate = bp["passed"] / bp["total"]
        if cur_rate < base_rate - 0.01:
            out["pearl_pass_rate_regression"] = {"current": cur_rate, "baseline": base_rate}
            out["warnings"].append("Pearl pass rate regressed vs baseline")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Robust, intelligent cohesive bestseller tester: 10k Pearl Prime + teacher-mode + v2 EI"
    )
    ap.add_argument("--read-all", action="store_true", help="Only read and print all config")
    ap.add_argument("--pearl-prime-input", "-i", default="", help="Pearl Prime 10k simulation JSON path")
    ap.add_argument("--teacher-matrix", action="store_true", help="Build teacher-mode test matrix")
    ap.add_argument("--teacher-matrix-cap", type=int, default=10_000, help="Cap teacher matrix size")
    ap.add_argument("--ei-v2-report", action="store_true", help="Include EI v2 rigorous eval report")
    ap.add_argument("--ei-v2-path", default="", help="Path to eval_rigorous_report.json")
    ap.add_argument("--run-pearl-10k", action="store_true", help="Run run_simulation_10k.py first")
    ap.add_argument("--run-pearl-timeout", type=int, default=600, help="Timeout (seconds) for run_simulation_10k")
    ap.add_argument("--llm", action="store_true", help="Call LLM for cohesive bestseller analysis")
    ap.add_argument("--dry-run", action="store_true", help="Skip LLM even if --llm")
    ap.add_argument("--out", "-o", default="", help="Output report dir")
    ap.add_argument("--require-100", action="store_true", help="Exit 1 if any bestseller-tier failure")
    ap.add_argument("--baseline", default="", help="Baseline report JSON for regression comparison")
    ap.add_argument("--ei-v2-threshold", type=float, default=EI_V2_DIMENSION_THRESHOLD, help="EI v2 dimension fail threshold")
    args = ap.parse_args()

    config = read_all_config()

    if args.read_all:
        print(json.dumps(config, indent=2, default=str))
        return 0

    pearl_path = Path(args.pearl_prime_input) if args.pearl_prime_input else REPO_ROOT / "artifacts" / "simulation_10k.json"
    if args.run_pearl_10k:
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "run_simulation_10k.py"), "--out", str(pearl_path)]
        try:
            r = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
                timeout=args.run_pearl_timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"run_simulation_10k timed out after {args.run_pearl_timeout}s", file=sys.stderr)
            return 1
        if r.returncode != 0:
            print("run_simulation_10k failed", file=sys.stderr)
            return r.returncode

    pearl_identified = None
    pearl_dims = None
    pearl_results = []
    pearl_summary = {}
    pearl_validation_errors: list[str] = []
    if pearl_path.exists():
        pearl_results, pearl_summary, pearl_validation_errors = load_pearl_prime_sim(pearl_path)
        if pearl_validation_errors:
            print("Warn: simulation validation:", pearl_validation_errors, file=sys.stderr)
        if pearl_results:
            pearl_identified = identify_bestseller_errors(pearl_results)
            pearl_dims = analyze_pearl_dimensions(pearl_results, pearl_summary)
    else:
        if args.pearl_prime_input or args.run_pearl_10k:
            print(f"Warn: Pearl sim not found: {pearl_path}", file=sys.stderr)

    teacher_matrix: list[dict] = []
    if args.teacher_matrix:
        teacher_matrix = build_teacher_mode_matrix(config, cap=args.teacher_matrix_cap)

    ei_v2_report = None
    if args.ei_v2_report:
        p = Path(args.ei_v2_path) if args.ei_v2_path else REPO_ROOT / "artifacts" / "ei_v2" / "eval_rigorous_report.json"
        ei_v2_report = load_ei_v2_report(p)
    ei_v2_dims = analyze_ei_v2_dimensions(ei_v2_report, threshold=args.ei_v2_threshold)

    severity = classify_severity(pearl_identified, pearl_dims)
    coverage = coverage_from_pearl_results(pearl_results) if pearl_results else {}
    health_score = compute_health_score(pearl_identified, pearl_dims, ei_v2_dims, len(teacher_matrix), config)

    report = {
        "config_read": {
            "personas_count": config["personas_count"],
            "topics_count": config["topics_count"],
            "teachers_count": config["teachers_count"],
            "structural_formats": config["structural_formats"],
            "runtime_formats": config["runtime_formats"],
        },
        "validation_errors": pearl_validation_errors,
        "health_score": health_score,
        "severity": severity,
        "pearl_prime_10k": None,
        "pearl_dimension_analysis": pearl_dims,
        "coverage": coverage,
        "teacher_mode_matrix_size": len(teacher_matrix),
        "ei_v2_included": ei_v2_report is not None,
        "ei_v2_dimension_analysis": ei_v2_dims,
        "llm_analysis": None,
    }

    if pearl_identified:
        report["pearl_prime_10k"] = {
            "total": pearl_identified["total"],
            "passed": pearl_identified["total_passed"],
            "failed": pearl_identified["total_failed"],
            "bestseller_failed": pearl_identified["bestseller_failed"],
            "error_reasons_summary": pearl_identified["error_reasons_summary"],
            "bestseller_errors_sample": pearl_identified["bestseller_errors"][:20],
        }

    baseline = load_baseline(Path(args.baseline)) if args.baseline else None
    if baseline:
        report["baseline_comparison"] = compare_to_baseline(report, baseline)

    if args.llm:
        prompt = build_llm_prompt(
            config, pearl_identified, pearl_dims, teacher_matrix,
            ei_v2_report, ei_v2_dims, severity, health_score,
        )
        llm_out = call_llm(prompt, args.dry_run)
        report["llm_analysis"] = llm_out
        if not llm_out.get("llm_skipped"):
            report["what_is_100_percent"] = llm_out.get("what_is_100_percent", [])
            report["bestseller_gaps"] = llm_out.get("bestseller_gaps", [])
            report["root_causes"] = llm_out.get("root_causes", [])

    out_dir = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "cohesive_bestseller_tester_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {report_path}")

    summary_lines = [
        "Cohesive Bestseller Tester (robust)",
        f"Health score: {health_score}/100",
        f"Config: {config['personas_count']} personas, {config['topics_count']} topics, {config['teachers_count']} teachers",
        f"Teacher-mode matrix: {len(teacher_matrix)} slots",
    ]
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = severity.get(sev, [])
        if items:
            summary_lines.append(f"  {sev}: {len(items)} — {[i.get('kind') for i in items]}")
    if pearl_identified:
        summary_lines.extend([
            "",
            f"Pearl Prime 10k: total={pearl_identified['total']} passed={pearl_identified['total_passed']} failed={pearl_identified['total_failed']} bestseller_failed={pearl_identified['bestseller_failed']}",
        ])
    if pearl_dims:
        summary_lines.append(f"  Pass rate: {pearl_dims.get('overall_pass_rate', 0):.1%}  Phase2/3 fails: {pearl_dims.get('phase2_failed_count', 0)}/{pearl_dims.get('phase3_failed_count', 0)}")
    if ei_v2_dims:
        fails = ei_v2_dims.get("dimension_fails", [])
        if fails:
            summary_lines.append(f"  EI v2 dimensions below threshold: {[d['dimension'] for d in fails]}")
    if report.get("baseline_comparison") and report["baseline_comparison"].get("warnings"):
        summary_lines.append("")
        summary_lines.append("Baseline regression: " + "; ".join(report["baseline_comparison"]["warnings"]))
    if report.get("llm_analysis") and not report["llm_analysis"].get("llm_skipped"):
        summary_lines.append("")
        summary_lines.append("LLM — what is 100%:")
        for s in report.get("what_is_100_percent", [])[:10]:
            summary_lines.append(f"  - {s}")
        summary_lines.append("LLM — root causes:")
        for rc in report.get("root_causes", [])[:5]:
            summary_lines.append(f"  - {rc.get('category', '')}: {rc.get('recommendation', '')}")
    summary_path = out_dir / "cohesive_bestseller_tester_SUMMARY.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"Wrote {summary_path}")

    if args.require_100 and pearl_identified and pearl_identified["bestseller_failed"] > 0:
        print(f"FAIL: {pearl_identified['bestseller_failed']} bestseller-tier failure(s) (100% gate)", file=sys.stderr)
        return 1
    if args.require_100 and severity.get("CRITICAL"):
        print("FAIL: CRITICAL severity issues present", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
