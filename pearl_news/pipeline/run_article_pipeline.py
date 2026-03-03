#!/usr/bin/env python3
"""
Pearl News — run full article pipeline: feeds → ingest → [classify → template select → assemble → QC].
Output: normalized feed items (and later draft articles) to --out-dir.

Usage:
  python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts
  python -m pearl_news.pipeline.run_article_pipeline --out-dir ./output --limit 10
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pearl_news.pipeline.feed_ingest import ingest_feeds
from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.pipeline.template_selector import select_templates
from pearl_news.pipeline.article_assembler import assemble_articles
from pearl_news.pipeline.quality_gates import run_quality_gates, filter_passed
from pearl_news.pipeline.qc_checklist import run_qc_checklist, filter_checklist_passed

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl News: feeds → draft articles")
    ap.add_argument(
        "--feeds",
        default=None,
        help="Path to feeds.yaml (default: pearl_news/config/feeds.yaml)",
    )
    ap.add_argument(
        "--out-dir",
        default="artifacts/pearl_news/drafts",
        help="Output directory for drafts and build manifest",
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
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    ap.add_argument(
        "--write-minimal-drafts",
        action="store_true",
        help="Write minimal article JSON per feed item (title, summary, featured_image) for testing WP post",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    feeds_path = Path(args.feeds) if args.feeds else root / "config" / "feeds.yaml"
    out_dir = Path(args.out_dir)

    if not feeds_path.exists():
        logger.error("Feeds config not found: %s", feeds_path)
        return 1

    if args.verbose:
        logging.getLogger("pearl_news").setLevel(logging.DEBUG)

    out_dir.mkdir(parents=True, exist_ok=True)
    # Metadata always goes to artifacts/pearl_news/ (fixed path per schema)
    artifact_dir = Path("artifacts/pearl_news")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Ingest feeds
    try:
        raw_items = ingest_feeds(feeds_path, limit=args.limit, per_feed_limit=args.per_feed_limit)
    except Exception as e:
        logger.exception("Feed ingest failed: %s", e)
        return 1

    logger.info("Ingested %d items", len(raw_items))

    # Step 2–6: Full pipeline (unless --write-minimal-drafts for quick test)
    if getattr(args, "write_minimal_drafts", False):
        # Shortcut: skip classify/assemble, write minimal drafts only
        articles_to_write: list[dict[str, Any]] = []
        for i, item in enumerate(raw_items):
            images = item.get("images") or []
            featured = None
            if images:
                img = images[0]
                featured = {
                    "url": img.get("url"),
                    "credit": img.get("credit") or item.get("source_feed_title", ""),
                    "source_url": img.get("source_url") or item.get("url", ""),
                }
                if img.get("caption"):
                    featured["caption"] = img["caption"]
            draft = {
                "title": item.get("title") or "(No title)",
                "content": f"<p>{item.get('summary') or item.get('raw_summary') or 'No summary.'}</p>",
                "slug": None,
                "featured_image": featured,
            }
            if item.get("url"):
                draft["content"] += f'<p><a href="{item["url"]}">Source</a></p>'
            draft["id"] = item.get("id", f"item_{i}")
            articles_to_write.append(draft)
    else:
        # Full pipeline: classify → select → assemble → quality gates → qc
        items = classify_sdgs(raw_items)
        items = select_templates(items)
        articles = assemble_articles(items)
        metadata_path = artifact_dir / "article_metadata.jsonl"
        articles = run_quality_gates(articles, metadata_path=metadata_path)
        articles = run_qc_checklist(articles)
        articles_to_write = filter_checklist_passed(filter_passed(articles))

        # Append article metadata for each assembled article (all, including failed)
        for draft in articles:
            article_id = draft.get("_feed_item_id", draft.get("id", ""))
            meta = {
                "article_id": str(article_id),
                "date": draft.get("pub_date") or datetime.now(timezone.utc).isoformat(),
                "topic": draft.get("topic") or "general",
                "primary_sdg": draft.get("primary_sdg") or "17",
                "template_id": draft.get("template_id") or "hard_news_spiritual_response",
                "teacher_ids": draft.get("teacher_ids") or [],
                "stressor_tags": draft.get("stressor_tags") or [],
                "region": draft.get("region") or "",
                "phrase_flags": draft.get("phrase_flags") or [],
            }
            with open(metadata_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")
        if articles:
            logger.info("Appended %d metadata lines to %s", len(articles), metadata_path)

    # Build manifest (audit trail): ingested items + build metadata
    build_date = datetime.now(timezone.utc).isoformat()
    manifest: dict[str, Any] = {
        "build_date": build_date,
        "feeds_path": str(feeds_path),
        "limit": args.limit,
        "per_feed_limit": args.per_feed_limit,
        "item_count": len(raw_items),
        "articles_count": len(articles_to_write),
        "items": raw_items,
    }
    manifest_path = out_dir / "ingest_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s", manifest_path)

    # Write each normalized item as a JSON file for downstream
    for i, item in enumerate(raw_items):
        item_id = item.get("id", f"item_{i}")
        item_path = out_dir / f"feed_item_{item_id}.json"
        item_path.write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write article drafts (minimal or full pipeline output)
    for i, draft in enumerate(articles_to_write):
        article_id = draft.get("_feed_item_id", draft.get("id", i))
        draft_clean = {k: v for k, v in draft.items() if not k.startswith("_")}
        draft_path = out_dir / f"article_{article_id}.json"
        draft_path.write_text(json.dumps(draft_clean, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %d article drafts", len(articles_to_write))

    logger.info("Pipeline complete. Output: %s (%d items, %d articles)", out_dir, len(raw_items), len(articles_to_write))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
