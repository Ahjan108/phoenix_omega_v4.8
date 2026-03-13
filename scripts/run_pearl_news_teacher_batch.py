#!/usr/bin/env python3
"""
Pearl News teacher batch runner.

Purpose:
- build one article per active teacher using the current deterministic Pearl News stack
- use live feed items when the current feed mix supports the teacher/topic assignment
- fall back to bounded topic fixtures when live feeds do not cover the needed topic

Canonical stage trace:
- docs/PEARL_NEWS_BATCH_PIPELINE_TRACE.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pearl_news.pipeline.assemble_v52 import assemble_v52
from pearl_news.pipeline.feed_ingest import ingest_feeds
from pearl_news.pipeline.news_cycle_slot_contract import (
    apply_completed_contract,
    build_slot_contract,
    load_completed_contract,
    validate_completed_contract,
    write_pending_contract,
)
from pearl_news.pipeline.news_action_resolver import resolve_news_actions
from pearl_news.pipeline.quality_gates import run_quality_gates
from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.teacher_adapter import build_news_payload
from pearl_prime.teacher_system import list_active_teacher_ids


PEARL_ROOT = REPO_ROOT / "pearl_news"
CONFIG_ROOT = PEARL_ROOT / "config"
FEEDS_PATH = CONFIG_ROOT / "feeds.yaml"
TRACE_DOC_PATH = "docs/PEARL_NEWS_BATCH_PIPELINE_TRACE.md"

TOPIC_TITLE_MAP = {
    "mental_health": "Mental Health",
    "education": "Education",
    "peace_conflict": "Peace and Conflict",
    "inequality": "Inequality",
    "climate": "Climate",
    "economy_work": "Work and Economy",
    "partnerships": "Global Partnerships",
    "general": "Global Affairs",
}

TOPIC_CONCEPT_MAP = {
    "mental_health": ("stabilizing practice", "steadies", "daily overwhelm"),
    "education": ("embodied learning frame", "restores", "focus under pressure"),
    "peace_conflict": ("conflict witness practice", "interrupts", "reactive fear"),
    "inequality": ("human dignity lens", "clarifies", "structural stress"),
    "climate": ("interdependence frame", "turns", "climate panic into grounded action"),
    "economy_work": ("right livelihood frame", "reframes", "work anxiety"),
    "partnerships": ("shared duty ethic", "translates", "global goals into local action"),
    "general": ("clear-seeing practice", "grounds", "news overload"),
}

TEACHER_BATCH_PLAN: dict[str, dict[str, str]] = {
    "ahjan": {"topic": "climate", "template_id": "commentary"},
    "channeler_junko": {"topic": "climate", "template_id": "hard_news_spiritual_response"},
    "joshin": {"topic": "education", "template_id": "youth_feature"},
    "maat": {"topic": "peace_conflict", "template_id": "explainer_context"},
    "master_feung": {"topic": "education", "template_id": "hard_news_spiritual_response"},
    "master_sha": {"topic": "mental_health", "template_id": "hard_news_spiritual_response"},
    "master_wu": {"topic": "education", "template_id": "youth_feature"},
    "miki": {"topic": "climate", "template_id": "hard_news_spiritual_response"},
    "omote": {"topic": "peace_conflict", "template_id": "hard_news_spiritual_response"},
    "pamela_fellows": {"topic": "mental_health", "template_id": "youth_feature"},
    "ra": {"topic": "peace_conflict", "template_id": "hard_news_spiritual_response"},
    "sai_ma": {"topic": "mental_health", "template_id": "explainer_context"},
}

TOPIC_FIXTURES: dict[str, dict[str, Any]] = {
    "climate": {
        "title": "UN report shows 2026 heat pressure is reshaping youth daily function",
        "summary": (
            "A new UN climate analysis says repeated heat exposure, school disruption, and community-level "
            "adaptation failures are already changing how young people sleep, study, and plan their futures."
        ),
        "url": "https://example.org/pearl-news-fixtures/climate-youth-function",
        "pub_date": "2026-03-12T12:00:00+00:00",
        "primary_sdg": "13",
        "un_body": "United Nations Environment Programme",
        "sdg_labels": {"13": "Climate Action"},
    },
    "education": {
        "title": "UNESCO warns digital strain is reducing attention and classroom confidence",
        "summary": (
            "UNESCO-linked reporting says constant digital interruption and post-pandemic learning gaps are "
            "reducing concentration, confidence, and classroom belonging for many students."
        ),
        "url": "https://example.org/pearl-news-fixtures/education-attention-strain",
        "pub_date": "2026-03-12T12:00:00+00:00",
        "primary_sdg": "4",
        "un_body": "UNESCO",
        "sdg_labels": {"4": "Quality Education"},
    },
    "mental_health": {
        "title": "WHO says young adults are reporting higher levels of exhaustion and social disconnection",
        "summary": (
            "A World Health Organization brief links rising exhaustion, doomscrolling, and social disconnection "
            "to reduced resilience and daily functioning among young adults."
        ),
        "url": "https://example.org/pearl-news-fixtures/mental-health-disconnection",
        "pub_date": "2026-03-12T12:00:00+00:00",
        "primary_sdg": "3",
        "un_body": "World Health Organization",
        "sdg_labels": {"3": "Good Health and Well-Being"},
    },
}


def _try_load_qwen_provider():
    """Attempt to import the Qwen slot provider (Lane 4). Returns None if unavailable."""
    try:
        from pearl_news.pipeline.slot_provider_qwen import QwenSlotProvider
        return QwenSlotProvider
    except ImportError:
        return None


def _fill_slots_with_qwen(pending_path: Path, slots_dir: Path) -> Path | None:
    """Fill a pending slot contract using Qwen. Returns completed contract path or None on failure."""
    provider_cls = _try_load_qwen_provider()
    if provider_cls is None:
        return None
    try:
        provider = provider_cls(config_root=CONFIG_ROOT)
        completed_path, errors = provider.process_contract(pending_path, slots_dir)
        if errors:
            print(
                f"Qwen provider returned incomplete contract for {pending_path.stem}: {', '.join(errors)}",
                file=sys.stderr,
            )
        return completed_path
    except Exception as exc:
        print(f"Qwen provider error: {exc}", file=sys.stderr)
        return None


def _headline_topic(topic: str) -> str:
    return TOPIC_TITLE_MAP.get(topic, topic.replace("_", " ").title() if topic else "Global Affairs")


def _build_contextual_title(item: dict[str, Any]) -> str:
    teacher = item.get("_teacher_resolved") or {}
    teacher_name = teacher.get("display_name") or "Forum Participant"
    topic = item.get("topic") or "general"
    concept, verb, outcome = TOPIC_CONCEPT_MAP.get(topic, TOPIC_CONCEPT_MAP["general"])
    problem = {
        "mental_health": "Gen Z Mental Overload",
        "education": "Gen Z Learning Burnout",
        "peace_conflict": "Gen Z Conflict Fatigue",
        "inequality": "Gen Z Inequality Stress",
        "climate": "Gen Z Climate Anxiety",
        "economy_work": "Gen Z Work Insecurity",
        "partnerships": "Gen Z Institutional Distrust",
        "general": "Gen Z Global Stress",
    }.get(topic, "Gen Z Global Stress")
    return f"{problem}: How {teacher_name}'s {concept} {verb} {outcome}"


def _replace_h1(content: str, new_title: str) -> str:
    import re

    if not content:
        return content
    if re.search(r"<h1[^>]*>.*?</h1>", content, re.IGNORECASE | re.DOTALL):
        return re.sub(
            r"<h1[^>]*>.*?</h1>",
            f"<h1>{new_title}</h1>",
            content,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return f"<h1>{new_title}</h1>\n\n{content}"


def _load_live_items(limit: int) -> dict[str, list[dict[str, Any]]]:
    items = classify_sdgs(ingest_feeds(FEEDS_PATH, limit=limit, per_feed_limit=limit))
    by_topic: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_topic[item.get("topic") or "general"].append(item)
    return by_topic


def _build_teacher_payload(teacher_id: str, topic: str) -> dict[str, Any]:
    result = build_news_payload(teacher_id, REPO_ROOT, topic, require_topic_in_roster=False)
    if result.payload is None:
        raise RuntimeError(f"no Pearl News teacher payload for {teacher_id} topic={topic}")
    payload = result.payload
    return {
        "teacher_id": teacher_id,
        "display_name": payload.teacher_name,
        "tradition": payload.tradition,
        "attribution": f"From within the {payload.tradition} tradition, {payload.teacher_name} teaches that",
        "atoms": payload.teacher_quotes[:3],
        "teacher_framework_term": payload.teacher_framework_term,
        "teacher_diagnostic_claim": payload.teacher_diagnostic_claim,
        "teacher_named_practice": payload.teacher_named_practice,
        "teacher_quotes": payload.teacher_quotes,
        "teacher_safety_boundary": payload.teacher_safety_boundary,
        "teacher_behavior_bridge": payload.teacher_behavior_bridge,
        "teacher_civic_bridge": payload.teacher_civic_bridge,
    }


def _pick_source_item(
    topic: str,
    teacher_id: str,
    live_items_by_topic: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any], str]:
    live_items = live_items_by_topic.get(topic) or []
    if live_items:
        idx = sum(ord(ch) for ch in teacher_id) % len(live_items)
        item = dict(live_items[idx])
        return item, "live_feed"
    fixture = TOPIC_FIXTURES.get(topic)
    if not fixture:
        raise RuntimeError(f"no live item or fixture available for topic={topic}")
    return dict(fixture), "fixture"


def _build_item(
    teacher_id: str,
    topic: str,
    template_id: str,
    source_item: dict[str, Any],
    source_mode: str,
) -> dict[str, Any]:
    teacher = _build_teacher_payload(teacher_id, topic)
    article_id = f"teacher_{teacher_id}_{topic}_{template_id}"
    raw_title = source_item.get("raw_title") or source_item.get("title") or f"{_headline_topic(topic)} update"
    raw_summary = source_item.get("raw_summary") or source_item.get("summary") or ""
    item = {
        "id": article_id,
        "template_id": template_id,
        "topic": topic,
        "primary_sdg": source_item.get("primary_sdg", "17"),
        "sdg_labels": source_item.get("sdg_labels") or {"17": "Partnerships for the Goals"},
        "un_body": source_item.get("un_body") or "United Nations",
        "raw_title": raw_title,
        "raw_summary": raw_summary,
        "title": raw_title,
        "summary": raw_summary,
        "url": source_item.get("url", ""),
        "pub_date": source_item.get("pub_date", ""),
        "language": "en",
        "source_feed_id": source_item.get("source_feed_id") or source_mode,
        "_teacher_resolved": teacher,
        "_batch_source_mode": source_mode,
        "_batch_source_title": raw_title,
    }
    if source_item.get("images"):
        item["images"] = source_item["images"]
    item["_news_actions"] = resolve_news_actions(item, teacher, pearl_config_root=CONFIG_ROOT)
    return item


def _render_article_payload(item: dict[str, Any]) -> dict[str, Any]:
    teacher = item.get("_teacher_resolved") or {}
    v52_input = {
        "slots": item["_v52_slots"],
        "teacher": teacher.get("display_name") or "Forum Participant",
        "topic": item.get("topic", "general"),
        "sdg": item.get("primary_sdg", "3"),
        "template": item.get("template_id", "hard_news_spiritual_response"),
        "news_event": item.get("summary") or item.get("raw_summary") or "",
        "_deterministic_teacher_topic_pack": item.get("_deterministic_teacher_topic_pack"),
        "_deterministic_beat_map": item.get("_deterministic_beat_map"),
        "_deterministic_article_plan": item.get("_deterministic_article_plan"),
    }
    compact_html = assemble_v52(v52_input, standalone=False)
    v52_html = assemble_v52(v52_input, standalone=True)
    title = _build_contextual_title(item)
    item["article_title"] = title
    item["content"] = _replace_h1(compact_html, title)
    preview_content = _replace_h1(v52_html, title)
    payload = {
        "title": title,
        "content": item["content"],
        "content_format": "v52",
        "content_render_mode": "compact",
        "slug": item["id"],
        "template_id": item["template_id"],
        "template": item["template_id"],
        "article_type": item["template_id"],
        "language": item["language"],
        "topic": item["topic"],
        "primary_sdg": item["primary_sdg"],
        "un_body": item["un_body"],
        "url": item["url"],
        "pub_date": item["pub_date"],
        "source_feed_id": item["source_feed_id"],
        "qc_passed": item.get("qc_passed", False),
        "qc_results": item.get("qc_results", {}),
        "teacher_used": {
            "teacher_id": teacher.get("teacher_id"),
            "display_name": teacher.get("display_name"),
            "tradition": teacher.get("tradition"),
        },
        "validation": {
            "passed": (item.get("_validation") or {}).get("passed"),
            "failed_gates": (item.get("_validation") or {}).get("failed_gates", []),
        },
        "exercise_payload": (item.get("_news_actions") or {}).get("exercise_payload"),
        "cta_payload": (item.get("_news_actions") or {}).get("cta_payload"),
        "freebies_payload": (item.get("_news_actions") or {}).get("freebies_payload"),
        "slots": item.get("_v52_slots"),
        "v52_slots": item.get("_v52_slots"),
        "build_meta": {
            "source_mode": item.get("_batch_source_mode"),
            "source_title": item.get("_batch_source_title"),
            "deterministic_pack": item.get("_deterministic_teacher_topic_pack"),
            "deterministic_beat_map": item.get("_deterministic_beat_map"),
            "deterministic_article_plan": item.get("_deterministic_article_plan"),
            "slot_source": item.get("_slot_source"),
            "slot_contract_path": item.get("_slot_contract_path"),
        },
    }
    payload["_preview_content"] = preview_content
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate one Pearl News article per active teacher.")
    ap.add_argument("--out-dir", default="artifacts/pearl_news/teacher_batch_latest", help="Output directory")
    ap.add_argument("--live-limit", type=int, default=40, help="Feed ingest limit when sourcing live items")
    ap.add_argument("--simulate", action="store_true", help="Use simulated expansion instead of Claude API")
    ap.add_argument(
        "--slot-source",
        choices=("file", "qwen", "auto"),
        default="file",
        help="Content source for remaining non-deterministic slots: file (local), qwen (provider), auto (file first, qwen fallback)",
    )
    ap.add_argument(
        "--slots-dir",
        default="",
        help="Slot contract directory. Defaults to <out-dir>/slots",
    )
    ap.add_argument(
        "--stop-after-contracts",
        action="store_true",
        help="Emit slot contracts and stop before assembly",
    )
    ap.add_argument(
        "--teacher",
        default="",
        help="Process only this teacher ID (skip all others)",
    )
    ap.add_argument(
        "--teacher-set",
        default="",
        help="Process only teachers in this comma-separated list or named set (all=all active teachers)",
    )
    args = ap.parse_args()

    out_dir = REPO_ROOT / args.out_dir
    articles_dir = out_dir / "articles"
    html_dir = out_dir / "html"
    meta_dir = out_dir / "_meta"
    slots_dir = REPO_ROOT / args.slots_dir if args.slots_dir else out_dir / "slots"
    articles_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    (slots_dir / "pending").mkdir(parents=True, exist_ok=True)
    (slots_dir / "completed").mkdir(parents=True, exist_ok=True)

    live_items_by_topic = _load_live_items(args.live_limit)
    active_teachers = list_active_teacher_ids(REPO_ROOT)

    if args.teacher:
        if args.teacher not in active_teachers:
            print(f"Warning: --teacher={args.teacher} not in active teachers, proceeding anyway", file=sys.stderr)
        active_teachers = [args.teacher]
    elif args.teacher_set:
        if args.teacher_set.lower() == "all":
            pass
        else:
            requested = [t.strip() for t in args.teacher_set.split(",") if t.strip()]
            active_teachers = [t for t in active_teachers if t in requested]
            if not active_teachers:
                print(f"Error: no matching teachers in --teacher-set={args.teacher_set}", file=sys.stderr)
                return 1

    batch_manifest: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for teacher_id in active_teachers:
        plan = TEACHER_BATCH_PLAN.get(teacher_id)
        if not plan:
            failures.append({"teacher_id": teacher_id, "error": "missing batch plan"})
            continue
        topic = plan["topic"]
        template_id = plan["template_id"]
        source_item, source_mode = _pick_source_item(topic, teacher_id, live_items_by_topic)
        try:
            item = _build_item(teacher_id, topic, template_id, source_item, source_mode)
            contract, deterministic_plan = build_slot_contract(item, REPO_ROOT)
            pending_path = write_pending_contract(contract, slots_dir)

            if args.stop_after_contracts:
                batch_manifest.append(
                    {
                        "teacher_id": teacher_id,
                        "template_id": template_id,
                        "topic": topic,
                        "source_mode": source_mode,
                        "source_title": source_item.get("title") or source_item.get("raw_title"),
                        "slot_source": "pending",
                        "slot_contract_path": str(pending_path.relative_to(REPO_ROOT)),
                        "status": "pending_writer_fill",
                        "pack_path": deterministic_plan.get("pack_path"),
                        "beat_map_id": deterministic_plan.get("beat_map_id"),
                    }
                )
                continue

            actual_slot_source = args.slot_source
            completed_contract = load_completed_contract(item["id"], slots_dir)

            if args.slot_source == "file":
                if not completed_contract:
                    raise RuntimeError(
                        f"missing completed slot contract for {item['id']} under {slots_dir.relative_to(REPO_ROOT)}"
                    )
            elif args.slot_source == "qwen":
                if completed_contract:
                    print(f"Info: using existing completed contract for {item['id']}", file=sys.stderr)
                else:
                    completed_path = _fill_slots_with_qwen(pending_path, slots_dir)
                    if not completed_path:
                        raise RuntimeError(
                            f"Qwen provider failed to fill contract for {item['id']}"
                        )
                    completed_contract = load_completed_contract(item["id"], slots_dir)
                    if not completed_contract:
                        raise RuntimeError(
                            f"Qwen provider did not produce valid contract for {item['id']}"
                        )
            elif args.slot_source == "auto":
                if completed_contract:
                    actual_slot_source = "file"
                else:
                    completed_path = _fill_slots_with_qwen(pending_path, slots_dir)
                    if completed_path:
                        completed_contract = load_completed_contract(item["id"], slots_dir)
                        actual_slot_source = "qwen"
                    if not completed_contract:
                        raise RuntimeError(
                            f"auto mode: no completed contract and Qwen provider unavailable for {item['id']}"
                        )

            completed_contract["_path"] = str(Path(completed_contract["_path"]).relative_to(REPO_ROOT))
            contract_errors = validate_completed_contract(completed_contract)
            if contract_errors:
                raise RuntimeError(
                    f"incomplete slot contract for {item['id']}: {', '.join(contract_errors)}"
                )
            item = apply_completed_contract(item, deterministic_plan, completed_contract)
            item["_slot_source"] = actual_slot_source
            item = run_quality_gates([item])[0]
            payload = _render_article_payload(item)
            json_path = articles_dir / f"article_{teacher_id}_{topic}_{template_id}.json"
            html_path = html_dir / f"article_{teacher_id}_{topic}_{template_id}_v52.html"
            preview_content = payload.pop("_preview_content", payload["content"])
            json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            html_path.write_text(preview_content, encoding="utf-8")
            batch_manifest.append(
                {
                    "teacher_id": teacher_id,
                    "template_id": template_id,
                    "topic": topic,
                    "source_mode": source_mode,
                    "source_title": source_item.get("title") or source_item.get("raw_title"),
                    "qc_passed": payload["qc_passed"],
                    "failed_gates": payload["validation"]["failed_gates"],
                    "pack_path": payload["build_meta"]["deterministic_pack"],
                    "beat_map_id": payload["build_meta"]["deterministic_beat_map"],
                    "slot_source": actual_slot_source,
                    "slot_contract_path": payload["build_meta"].get("slot_contract_path") or str(pending_path.relative_to(REPO_ROOT)),
                    "json_path": str(json_path.relative_to(REPO_ROOT)),
                    "html_path": str(html_path.relative_to(REPO_ROOT)),
                }
            )
        except Exception as exc:
            failures.append({"teacher_id": teacher_id, "topic": topic, "template_id": template_id, "error": str(exc)})

    report = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "simulate": bool(args.simulate),
        "slot_source": args.slot_source,
        "slots_dir": str(slots_dir.relative_to(REPO_ROOT)),
        "stop_after_contracts": bool(args.stop_after_contracts),
        "teacher_filter": args.teacher or args.teacher_set or "all",
        "active_teacher_count": len(active_teachers),
        "articles_built": len(batch_manifest),
        "live_topics_available": {topic: len(items) for topic, items in live_items_by_topic.items()},
        "pipeline_contract": {
            "trace_doc": TRACE_DOC_PATH,
            "entry_point": "scripts/run_pearl_news_teacher_batch.py",
            "pre_review_runner": "scripts/ci/check_pearl_news_pre_review.py",
            "architecture": "slot-file",
            "slot_modes": ["file", "qwen", "auto"],
            "stages": [
                {
                    "stage": 1,
                    "name": "active_teacher_authority",
                    "file": "pearl_prime/teacher_system/__init__.py",
                },
                {
                    "stage": 2,
                    "name": "feed_ingest",
                    "file": "pearl_news/pipeline/feed_ingest.py",
                },
                {
                    "stage": 3,
                    "name": "topic_sdg_classification",
                    "file": "pearl_news/pipeline/topic_sdg_classifier.py",
                },
                {
                    "stage": 4,
                    "name": "teacher_payload_build",
                    "file": "pearl_news/teacher_adapter/adapter.py",
                },
                {
                    "stage": 5,
                    "name": "deterministic_pack_and_beat_map_resolution",
                    "file": "pearl_news/pipeline/deterministic_teacher_topic.py",
                },
                {
                    "stage": 6,
                    "name": "slot_contract_emit",
                    "file": "pearl_news/pipeline/news_cycle_slot_contract.py",
                },
                {
                    "stage": 7,
                    "name": "slot_fill",
                    "mode": args.slot_source,
                    "files": {
                        "file": "manual writer fills slots/<article_id>.yaml",
                        "qwen": "pearl_news/pipeline/slot_provider_qwen.py",
                        "auto": "file with qwen fallback",
                    },
                },
                {
                    "stage": 8,
                    "name": "slot_contract_apply",
                    "file": "pearl_news/pipeline/news_cycle_slot_contract.py",
                },
                {
                    "stage": 9,
                    "name": "quality_gates",
                    "file": "pearl_news/pipeline/quality_gates.py",
                },
                {
                    "stage": 10,
                    "name": "news_action_resolution",
                    "file": "pearl_news/pipeline/news_action_resolver.py",
                },
                {
                    "stage": 11,
                    "name": "v52_render",
                    "file": "pearl_news/pipeline/assemble_v52.py",
                },
            ],
        },
        "batch_manifest": batch_manifest,
        "failures": failures,
        "files_used": {
            "active_teacher_authority": "pearl_prime/teacher_system/__init__.py",
            "live_feed_ingest": "pearl_news/pipeline/feed_ingest.py",
            "topic_classifier": "pearl_news/pipeline/topic_sdg_classifier.py",
            "teacher_payload": "pearl_news/teacher_adapter/adapter.py",
            "deterministic_packs": "pearl_news/pipeline/deterministic_teacher_topic.py",
            "slot_contract": "pearl_news/pipeline/news_cycle_slot_contract.py",
            "slot_provider_qwen": "pearl_news/pipeline/slot_provider_qwen.py",
            "quality_gates": "pearl_news/pipeline/quality_gates.py",
            "actions": "pearl_news/pipeline/news_action_resolver.py",
            "v52_renderer": "pearl_news/pipeline/assemble_v52.py",
        },
    }
    (meta_dir / "teacher_batch_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
