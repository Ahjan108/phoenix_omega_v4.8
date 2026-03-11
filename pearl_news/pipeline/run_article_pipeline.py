#!/usr/bin/env python3
"""
Pearl News — full pipeline: feeds → ingest → classify → template select → assemble → quality gates.
Output: final article drafts (title, content, metadata) to --out-dir; build manifests for audit.

Flags:
  --language    Generate articles in a specific language (en / zh-cn / ja). Default: en.
  --expand      LLM expansion (injects teacher, research, language, audience into prompt).

Usage:
  # Default English with LLM expansion
  python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts/en --expand

  # No LLM (fast draft only)
  python -m pearl_news.pipeline.run_article_pipeline --out-dir artifacts/pearl_news/drafts --limit 10
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from pearl_news.pipeline.feed_ingest import ingest_feeds
from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.pipeline.template_selector import select_templates
from pearl_news.pipeline.article_assembler import assemble_articles
from pearl_news.pipeline.llm_expand import run_expansion
from pearl_news.pipeline.quality_gates import run_quality_gates
from pearl_news.pipeline.teacher_resolver import resolve_teacher
from pearl_news.pipeline.news_action_resolver import resolve_news_actions, render_news_action_block

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {"en", "ja", "zh-cn"}
LANGUAGE_LABELS = {
    "en": "English",
    "ja": "Japanese",
    "zh-cn": "Simplified Chinese",
}

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
    "mental_health": ("attention reset", "steadies", "daily overwhelm"),
    "education": ("deep practice", "restores", "learning focus"),
    "peace_conflict": ("right speech", "interrupts", "reactive polarization"),
    "inequality": ("human dignity lens", "confronts", "normalized exclusion"),
    "climate": ("interdependence lens", "turns", "climate panic into grounded action"),
    "economy_work": ("right livelihood frame", "reframes", "work-related anxiety"),
    "partnerships": ("shared duty ethic", "translates", "global goals into local action"),
    "general": ("clear-seeing practice", "clarifies", "news-era confusion"),
}


def _headline_topic(topic: str) -> str:
    return TOPIC_TITLE_MAP.get(topic, topic.replace("_", " ").title() if topic else "Global Affairs")


def _build_contextual_title(item: dict[str, Any]) -> str:
    """
    Build non-RSS headline in required format:
    [Specific Gen Z problem]: How [Teacher Name]'s [concept] [verb] [outcome]
    """
    teacher = item.get("_teacher_resolved") or {}
    teacher_name = teacher.get("display_name") or "Forum Teacher"
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


def _inject_action_block(content: str, action_block_html: str) -> str:
    """Insert action block before Source line so source remains final."""
    if not action_block_html:
        return content
    marker = "<p><em>Source:"
    idx = content.find(marker)
    if idx == -1:
        return content.rstrip() + action_block_html
    return content[:idx].rstrip() + action_block_html + "\n" + content[idx:]


def _qc_failed_gate_ids(item: dict[str, Any]) -> list[str]:
    qc = item.get("qc_results") or {}
    return [
        gate for gate, status in qc.items()
        if gate != "timestamp" and status == "FAIL"
    ]


def _build_repair_feedback(item: dict[str, Any]) -> str:
    parts: list[str] = []
    if item.get("_expansion_failed"):
        parts.append("Expansion failed previously. Produce complete HTML and preserve all required sections.")
    failed_validation = (item.get("_validation") or {}).get("failed_gates") or []
    if failed_validation:
        parts.append(f"Fix validation gates: {', '.join(failed_validation)}.")
    failed_qc = _qc_failed_gate_ids(item)
    if failed_qc:
        parts.append(f"Fix quality gates: {', '.join(failed_qc)}.")
    if not parts:
        parts.append("Improve clarity, specificity, and compliance while preserving facts and source line.")
    return " ".join(parts)


def _is_llm_connectivity_failure(item: dict[str, Any]) -> bool:
    if not item.get("_expansion_failed"):
        return False
    msg = str(item.get("_expansion_error") or "").lower()
    if not msg:
        return True
    connectivity_markers = [
        "connect", "connection", "timeout", "timed out", "refused",
        "unreachable", "network", "503", "502", "api connection",
    ]
    return any(marker in msg for marker in connectivity_markers)


def _build_manifest_item(item: dict[str, Any]) -> dict[str, Any]:
    """One entry for build manifest (audit trail)."""
    teacher = item.get("_teacher_resolved") or {}
    validation = item.get("_validation") or {}
    return {
        "article_id": item.get("id", ""),
        "language": item.get("language", "en"),
        "feed_item": {
            "id": item.get("id", ""),
            "url": item.get("url", ""),
            "title": item.get("article_title") or item.get("title", ""),
            "published": item.get("pub_date", ""),
        },
        "template_id": item.get("template_id", ""),
        "atom_ids_used": {
            "news_event": [item.get("id", "")],
            "youth_impact": [],
            "teacher_quotes_practices": [teacher.get("teacher_id")] if teacher.get("teacher_id") else [],
            "sdg_refs": [item.get("primary_sdg", "")],
        },
        "teacher_used": {
            "teacher_id": teacher.get("teacher_id"),
            "display_name": teacher.get("display_name"),
            "tradition": teacher.get("tradition"),
        },
        "expansion": {
            "ran": item.get("_expansion_failed") is not None or bool(item.get("content")),
            "failed": item.get("_expansion_failed", False),
            "retries": item.get("_expansion_retries", 0),
        },
        "validation": {
            "passed": validation.get("passed"),
            "failed_gates": validation.get("failed_gates", []),
            "gate_count": validation.get("gate_count"),
            "passed_count": validation.get("passed_count"),
        },
        "action_payload": {
            "exercise_id": (item.get("_news_actions") or {}).get("exercise_payload", {}).get("exercise_id"),
            "mode": (item.get("_news_actions") or {}).get("mode"),
            "freebie_count": len((item.get("_news_actions") or {}).get("freebies_payload") or []),
            "missing_required": (item.get("_news_actions") or {}).get("missing_required", []),
        },
        "model_used": "lm_studio/qwen",
        "prompt_version": "expansion_system_v2",
        "qc_results": item.get("qc_results") or {},
        "signatures": {
            "headline_sig": item.get("headline_sig", ""),
            "lede_sig": item.get("lede_sig", ""),
            "teacher_sig": teacher.get("teacher_id", ""),
            "sdg_sig": item.get("primary_sdg", ""),
        },
        "built_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl News: feeds → draft articles")
    ap.add_argument(
        "--feeds",
        default=None,
        help="Path to feeds.yaml (default: pearl_news/config/feeds.yaml)",
    )
    ap.add_argument(
        "--out-dir",
        default=None,
        help="Output directory for drafts (default: artifacts/pearl_news/drafts/<language>)",
    )
    ap.add_argument(
        "--language",
        default="en",
        choices=sorted(SUPPORTED_LANGUAGES) + ["all"],
        help="Article language: en (default), ja, zh-cn, or all (runs 3 language passes)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of feed items to process (across all feeds)",
    )
    ap.add_argument(
        "--per-feed-limit",
        type=int,
        default=None,
        help="Max items per feed (before global --limit)",
    )
    ap.add_argument(
        "--no-filter-qc",
        action="store_true",
        help="Output all articles (including QC-failed); default is only QC-passed",
    )
    ap.add_argument(
        "--expand",
        action="store_true",
        help="Run LLM expansion (v2: injects teacher, research excerpt, language, audience)",
    )
    ap.add_argument(
        "--strict-publish-grade",
        action="store_true",
        help="Fail hard unless all items pass expansion+validation+QC; no fallback output.",
    )
    ap.add_argument(
        "--repair-max-attempts",
        type=int,
        default=2,
        help="Strict mode: max rewrite repair rounds for failed items (default: 2).",
    )
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger("pearl_news").setLevel(logging.DEBUG)

    root = Path(__file__).resolve().parent.parent
    feeds_path = Path(args.feeds) if args.feeds else root / "config" / "feeds.yaml"

    if not feeds_path.exists():
        logger.error("Feeds config not found: %s", feeds_path)
        return 1

    # If --language all, run pipeline once per language and report
    if args.language == "all":
        results = {}
        for lang in sorted(SUPPORTED_LANGUAGES):
            logger.info("=== Running pipeline for language: %s ===", lang)
            lang_args_list = [
                f"--language={lang}",
                f"--out-dir=artifacts/pearl_news/drafts/{lang}",
            ]
            if args.feeds:
                lang_args_list.append(f"--feeds={args.feeds}")
            if args.limit:
                lang_args_list.append(f"--limit={args.limit}")
            if args.expand:
                lang_args_list.append("--expand")
            if args.strict_publish_grade:
                lang_args_list.append("--strict-publish-grade")
                lang_args_list.append(f"--repair-max-attempts={args.repair_max_attempts}")
            if args.verbose:
                lang_args_list.append("--verbose")
            if args.no_filter_qc:
                lang_args_list.append("--no-filter-qc")
            import sys
            old_argv = sys.argv
            sys.argv = ["run_article_pipeline"] + lang_args_list
            exit_code = main()
            sys.argv = old_argv
            results[lang] = exit_code
        failed = [lang for lang, code in results.items() if code != 0]
        if failed:
            logger.error("Pipeline failed for languages: %s", failed)
            return 1
        logger.info("All-language pipeline complete: %s", results)
        return 0

    language = args.language.lower()
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path(f"artifacts/pearl_news/drafts/{language}")

    out_dir.mkdir(parents=True, exist_ok=True)
    config_root = root / "config"
    atoms_root = root / "atoms" / "teacher_quotes_practices"

    logger.info(
        "Pipeline start: language=%s out_dir=%s expand=%s strict=%s",
        language, out_dir, args.expand, args.strict_publish_grade,
    )

    if args.strict_publish_grade and not args.expand:
        logger.error("--strict-publish-grade requires --expand")
        return 1

    # Step 1: Ingest
    try:
        items = ingest_feeds(feeds_path, limit=args.limit, per_feed_limit=args.per_feed_limit)
    except Exception as e:
        logger.exception("Feed ingest failed: %s", e)
        return 1
    logger.info("Ingested %d items", len(items))

    if not items:
        logger.warning("No items to process; writing empty manifest.")
        manifest = {
            "build_date": datetime.now(timezone.utc).isoformat(),
            "language": language,
            "feeds_path": str(feeds_path),
            "item_count": 0,
            "articles_count": 0,
            "items": [],
            "build_manifests": [],
        }
        (out_dir / "ingest_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 0

    # Attach language to each item (used by assembler, resolver, expansion)
    for item in items:
        item["language"] = language

    # Step 2: Classify (topic + SDG)
    items = classify_sdgs(items)
    # Step 3: Select template
    items = select_templates(items)
    # Step 4: Assemble (structural draft from template + atoms/placeholders)
    items = assemble_articles(items)

    # Step 4a (NEW): Resolve named teacher per article
    for item in items:
        teacher = resolve_teacher(item, config_root=config_root, atoms_root=atoms_root)
        item["_teacher_resolved"] = teacher
        actions = resolve_news_actions(item, teacher, pearl_config_root=config_root)
        item["_news_actions"] = actions

    # Refine H1/article titles so they are contextual (not RSS-title restatements).
    for item in items:
        new_title = _build_contextual_title(item)
        item["article_title"] = new_title
        item["content"] = _replace_h1(item.get("content") or "", new_title)

    # Step 4b/5: Expansion + QC (with strict repair loop if enabled)
    repair_round = 0
    max_rounds = max(0, int(args.repair_max_attempts)) if args.strict_publish_grade else 0
    while True:
        if args.expand:
            items = run_expansion(items, config_root=config_root)
        items = run_quality_gates(items)

        failed_ids: list[str] = []
        for item in items:
            article_id = str(item.get("id") or "")
            actions = item.get("_news_actions") or {}
            missing_action_payload = bool(actions.get("missing_required"))
            if missing_action_payload:
                validation = item.setdefault("_validation", {"passed": False, "failed_gates": []})
                failed_gates = validation.setdefault("failed_gates", [])
                for g in ("teacher_bound_exercise", "cta_payload", "freebies_payload"):
                    if g not in failed_gates:
                        failed_gates.append(g)
                item["_validation_failed"] = True
                item["_needs_manual_review"] = True

            failed = (
                bool(item.get("_expansion_failed"))
                or bool(item.get("_validation_failed"))
                or (not item.get("qc_passed", False))
                or missing_action_payload
            )
            if failed:
                failed_ids.append(article_id)
                item["_repair_feedback"] = _build_repair_feedback(item)
                item["_needs_manual_review"] = True

        if not failed_ids:
            break
        if not args.strict_publish_grade or repair_round >= max_rounds:
            break

        repair_round += 1
        logger.warning(
            "Strict publish-grade repair round %d/%d for failed articles: %s",
            repair_round, max_rounds, ", ".join(failed_ids),
        )
        for item in items:
            if str(item.get("id") or "") in failed_ids:
                item["_expansion_failed"] = False
                item["_validation_failed"] = False

    # Step 6: Quality gates (filter to passed only unless --no-filter-qc)
    articles_to_output = [i for i in items if i.get("qc_passed") or args.no_filter_qc]

    strict_failures = [
        item for item in items
        if item.get("_expansion_failed") or item.get("_validation_failed") or (not item.get("qc_passed", False))
    ]
    if args.strict_publish_grade and strict_failures:
        failure_report = {
            "language": language,
            "strict_publish_grade": True,
            "repair_rounds_used": repair_round,
            "failed_count": len(strict_failures),
            "failed_items": [
                {
                    "id": i.get("id"),
                    "title": i.get("article_title") or i.get("title"),
                    "expansion_failed": bool(i.get("_expansion_failed")),
                    "expansion_error": i.get("_expansion_error"),
                    "validation_failed_gates": (i.get("_validation") or {}).get("failed_gates", []),
                    "qc_failed_gates": _qc_failed_gate_ids(i),
                    "llm_connectivity_blocked": _is_llm_connectivity_failure(i),
                }
                for i in strict_failures
            ],
        }
        failure_path = out_dir / "strict_publish_grade_failures.json"
        failure_path.write_text(json.dumps(failure_report, indent=2, ensure_ascii=False), encoding="utf-8")

        connectivity_blocked = any(_is_llm_connectivity_failure(i) for i in strict_failures)
        if connectivity_blocked:
            retry_flag = {
                "status": "blocked_waiting_for_llm_connectivity",
                "language": language,
                "retry_when": "llm_connectivity_restored",
                "failure_report": str(failure_path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            (out_dir / "llm_retry_pending.json").write_text(
                json.dumps(retry_flag, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        logger.error(
            "Strict publish-grade failed: %d article(s) did not pass expansion/validation/QC. See %s",
            len(strict_failures), failure_path,
        )
        return 1

    # Ingest manifest
    build_date = datetime.now(timezone.utc).isoformat()
    ingest_manifest = {
        "build_date": build_date,
        "language": language,
        "feeds_path": str(feeds_path),
        "limit": args.limit,
        "per_feed_limit": args.per_feed_limit,
        "item_count": len(items),
        "articles_passed_qc": sum(1 for i in items if i.get("qc_passed")),
        "articles_validation_failed": sum(1 for i in items if i.get("_validation_failed")),
        "articles_output": len(articles_to_output),
        "items": [
            {
                "id": i.get("id"),
                "title": i.get("title"),
                "topic": i.get("topic"),
                "language": i.get("language"),
                "qc_passed": i.get("qc_passed"),
                "validation_passed": (i.get("_validation") or {}).get("passed"),
                "teacher": (i.get("_teacher_resolved") or {}).get("display_name"),
            }
            for i in items
        ],
    }
    (out_dir / "ingest_manifest.json").write_text(
        json.dumps(ingest_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Wrote %s", out_dir / "ingest_manifest.json")

    # Author rotation (default author ID 1; extend list for multi-author rotation)
    author_ids = [1]

    # Build manifests + article JSON output
    build_manifests = []
    for i, item in enumerate(articles_to_output):
        article_id = item.get("id", "")
        lang_suffix = f"_{language}" if language != "en" else ""
        output_filename = f"article_{article_id}{lang_suffix}.json"

        author_id = author_ids[i % len(author_ids)] if author_ids else None
        template_id = item.get("template_id") or "hard_news_spiritual_response"

        # Featured image: prefer resolved image metadata, then feed image
        featured_image_data = item.get("_featured_image")
        featured_image = None
        featured_image_url = None
        featured_image_path = None

        if featured_image_data:
            if featured_image_data.get("url"):
                featured_image_url = featured_image_data["url"]
                featured_image = {
                    "url": featured_image_data["url"],
                    "alt_text": featured_image_data.get("alt_text", ""),
                    "caption": featured_image_data.get("caption", ""),
                }
            elif featured_image_data.get("path"):
                featured_image_path = featured_image_data["path"]
        else:
            # Fallback: use feed image if available
            feed_images = item.get("images") or []
            if feed_images and isinstance(feed_images[0], dict) and feed_images[0].get("url"):
                featured_image = feed_images[0]

        teacher = item.get("_teacher_resolved") or {}
        validation = item.get("_validation") or {}

        article_payload = {
            "title": item.get("article_title") or item.get("title", ""),
            "content": _inject_action_block(
                item.get("content", ""),
                render_news_action_block(item.get("_news_actions") or {}),
            ),
            "slug": article_id + lang_suffix,
            "author": author_id,
            "article_type": template_id,
            "language": language,
            "topic": item.get("topic", ""),
            "primary_sdg": item.get("primary_sdg", ""),
            "un_body": item.get("un_body", ""),
            "url": item.get("url", ""),
            "pub_date": item.get("pub_date", ""),
            "source_feed_id": item.get("source_feed_id", ""),
            "qc_passed": item.get("qc_passed", False),
            "qc_results": item.get("qc_results", {}),
            "teacher_used": {
                "teacher_id": teacher.get("teacher_id"),
                "display_name": teacher.get("display_name"),
                "tradition": teacher.get("tradition"),
            },
            "validation": {
                "passed": validation.get("passed"),
                "failed_gates": validation.get("failed_gates", []),
            },
            "needs_manual_review": item.get("_needs_manual_review", False),
            "exercise_payload": (item.get("_news_actions") or {}).get("exercise_payload"),
            "cta_payload": (item.get("_news_actions") or {}).get("cta_payload"),
            "freebies_payload": (item.get("_news_actions") or {}).get("freebies_payload"),
        }
        if featured_image:
            article_payload["featured_image"] = featured_image
        if featured_image_url:
            article_payload["featured_image_url"] = featured_image_url
        if featured_image_path:
            article_payload["featured_image_path"] = featured_image_path

        (out_dir / output_filename).write_text(
            json.dumps(article_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        build_manifests.append(_build_manifest_item(item))

    (out_dir / "build_manifests.json").write_text(
        json.dumps(build_manifests, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(
        "Wrote %d article drafts (%s) and build_manifests.json",
        len(articles_to_output), language,
    )

    # Manual review queue: articles that need human review
    needs_review = [
        {
            "article_id": item.get("id"),
            "language": language,
            "title": item.get("article_title") or item.get("title"),
            "topic": item.get("topic"),
            "failed_gates": (item.get("_validation") or {}).get("failed_gates", []),
            "expansion_failed": item.get("_expansion_failed", False),
            "queued_at": build_date,
        }
        for item in items
        if item.get("_needs_manual_review")
    ]
    if needs_review:
        review_queue_path = out_dir / "manual_review_queue.json"
        review_queue_path.write_text(
            json.dumps(needs_review, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.warning(
            "%d articles flagged for manual review → %s", len(needs_review), review_queue_path
        )

    logger.info(
        "Pipeline complete [%s]: %d items → %d articles (%d need review)",
        language, len(items), len(articles_to_output), len(needs_review),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
