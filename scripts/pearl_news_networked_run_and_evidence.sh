#!/usr/bin/env bash
# Pearl News — one real networked run from live feeds, then write evidence for GO/NO-GO.
# Run from repo root after: pip install feedparser pyyaml
# Usage: ./scripts/pearl_news_networked_run_and_evidence.sh [--limit N]

set -e
LIMIT=5
if [[ "${1:-}" == --limit && -n "${2:-}" ]]; then LIMIT="$2"; fi

OUT_DIR="${OUT_DIR:-artifacts/pearl_news/drafts}"
EVIDENCE_DIR="${EVIDENCE_DIR:-artifacts/pearl_news/evaluation}"
mkdir -p "$OUT_DIR" "$EVIDENCE_DIR"

echo "Running Pearl News pipeline (networked, limit=$LIMIT)..."
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --feeds pearl_news/config/feeds.yaml \
  --out-dir "$OUT_DIR" \
  --limit "$LIMIT"

COUNT=$(ls -1 "$OUT_DIR"/article_*.json 2>/dev/null | wc -l)
echo "Articles written: $COUNT"

# Evidence file for GO/NO-GO checklist
EVIDENCE_FILE="$EVIDENCE_DIR/networked_run_evidence.json"
PYTHONPATH=. python3 -c "
import json
from pathlib import Path
from datetime import datetime, timezone
out = Path('$OUT_DIR')
manifest = out / 'ingest_manifest.json'
evidence = {
    'run_at': datetime.now(timezone.utc).isoformat(),
    'out_dir': '$OUT_DIR',
    'limit': $LIMIT,
    'article_count': $COUNT,
    'ingest_manifest_exists': manifest.exists(),
}
if manifest.exists():
    with open(manifest) as f:
        data = json.load(f)
    evidence['item_count'] = data.get('item_count', 0)
    evidence['articles_output'] = data.get('articles_output', 0)
Path('$EVIDENCE_FILE').parent.mkdir(parents=True, exist_ok=True)
with open('$EVIDENCE_FILE', 'w') as f:
    json.dump(evidence, f, indent=2)
print('Evidence written to $EVIDENCE_FILE')
"
echo "Done. For GO/NO-GO: record this run (e.g. log or path to $EVIDENCE_FILE) in docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md Evidence section."
