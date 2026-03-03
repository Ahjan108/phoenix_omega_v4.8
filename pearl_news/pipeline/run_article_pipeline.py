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

# Stubs for next steps (implement and chain):
# from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
# from pearl_news.pipeline.template_selector import select_templates
# from pearl_news.pipeline.article_assembler import assemble_articles
# from pearl_news.pipeline.quality_gates import run_quality_gates
# from pearl_news.pipeline.qc_checklist import run_qc_checklist

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

    # Step 1: Ingest feeds
    try:
        items = ingest_feeds(feeds_path, limit=args.limit, per_feed_limit=args.per_feed_limit)
    except Exception as e:
        logger.exception("Feed ingest failed: %s", e)
        return 1

    logger.info("Ingested %d items", len(items))

    # Step 2+: Stubs — implement and uncomment to chain
    # items = classify_sdgs(items)       # Assign topic/SDG from sdg_news_topic_mapping + keyword or LLM
    # items = select_templates(items)    # Pick template per item from template_diversity config
    # items = assemble_articles(items)    # Render from template + atoms; optional LLM expansion
    # items = run_quality_gates(items)   # legal_boundary, editorial_firewall, quality_gates (fail-hard)
    # run_qc_checklist(items)            # Final validation; filter to passed only

    # Build manifest (audit trail): ingested items + build metadata
    build_date = datetime.now(timezone.utc).isoformat()
    manifest: dict[str, Any] = {
        "build_date": build_date,
        "feeds_path": str(feeds_path),
        "limit": args.limit,
        "per_feed_limit": args.per_feed_limit,
        "item_count": len(items),
        "items": items,
    }
    manifest_path = out_dir / "ingest_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s", manifest_path)

    # Write each normalized item as a JSON file for downstream (classifier can read these)
    for i, item in enumerate(items):
        item_id = item.get("id", f"item_{i}")
        item_path = out_dir / f"feed_item_{item_id}.json"
        item_path.write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")

    # Optional: write minimal article drafts (title + summary + featured_image from first image) for testing
    if getattr(args, "write_minimal_drafts", False):
        for i, item in enumerate(items):
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
            draft: dict[str, Any] = {
                "title": item.get("title") or "(No title)",
                "content": f"<p>{item.get('summary') or item.get('raw_summary') or 'No summary.'}</p>",
                "slug": None,
                "featured_image": featured,
            }
            if item.get("url"):
                draft["content"] += f'<p><a href="{item["url"]}">Source</a></p>'
            draft_path = out_dir / f"article_{item.get('id', i)}.json"
            draft_path.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Wrote minimal article drafts (with featured_image when available) for testing")

    logger.info("Pipeline step 1 complete. Output: %s (%d items)", out_dir, len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
