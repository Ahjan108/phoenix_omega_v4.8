#!/usr/bin/env bash
set -euo pipefail

# One-command Pearl News run:
# 1) tests
# 2) pipeline draft generation
# 3) optional WordPress post (draft)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="python3"
if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
fi

echo "[1/3] Running Pearl News tests..."
if [ -d test_pearl_news ]; then
  PYTHONPATH=. "$PY" -m pytest test_pearl_news/ -v -k "not real_rss"
elif [ -d tests/test_pearl_news ]; then
  PYTHONPATH=. "$PY" -m pytest tests/test_pearl_news/ -v -k "not real_rss"
else
  echo "No Pearl News test dir found"
  exit 1
fi

echo "[2/3] Running Pearl News pipeline..."
"$PY" -m pearl_news.pipeline.run_article_pipeline \
  --feeds pearl_news/config/feeds.yaml \
  --out-dir artifacts/pearl_news/drafts \
  --limit 10

if [ "${1:-}" = "--post" ]; then
  echo "[3/3] Posting first draft to WordPress as draft..."
  first=$(ls -1 artifacts/pearl_news/drafts/article_*.json | head -1)
  if [ -z "${first:-}" ]; then
    echo "No article_*.json generated"
    exit 1
  fi
  "$PY" scripts/pearl_news_post_to_wp.py --article "$first" --status draft
else
  echo "[3/3] Skipped WordPress post (pass --post to enable)."
fi

echo "Done."
