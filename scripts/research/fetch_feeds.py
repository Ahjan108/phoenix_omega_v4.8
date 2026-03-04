#!/usr/bin/env python3
"""
Fetch RSS feeds from config/research/youth_feed_sources.yaml and write to
artifacts/research/raw/<date>/ for use in generational research prompts.
"""
from __future__ import annotations

import argparse
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "research" / "youth_feed_sources.yaml"
ARTIFACTS_RAW = REPO_ROOT / "artifacts" / "research" / "raw"


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise SystemExit("pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def fetch_url(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "PearlNewsResearch/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to youth_feed_sources.yaml")
    parser.add_argument("--out-dir", default=None, help="Override output dir (default: artifacts/research/raw/<date>)")
    args = parser.parse_args()

    config = load_yaml(Path(args.config))
    rss_list = config.get("rss") or []
    if not rss_list:
        print("No rss entries in config")
        return

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    out_dir = Path(args.out_dir) if args.out_dir else ARTIFACTS_RAW / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    for entry in rss_list:
        feed_id = entry.get("id", "unknown")
        url = entry.get("url")
        if not url:
            continue
        try:
            content = fetch_url(url)
            out_file = out_dir / f"{feed_id}.xml"
            out_file.write_text(content, encoding="utf-8")
            print(f"Fetched {feed_id} -> {out_file}")
        except Exception as e:
            print(f"Skip {feed_id}: {e}")

    print(f"Wrote to {out_dir}")


if __name__ == "__main__":
    main()
