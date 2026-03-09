#!/usr/bin/env python3
"""
Requeue stale jobs — move jobs that have been in processing longer than stale_seconds back to the queue.
Run on schedule (e.g. every 15 min). Reads processing_key hash; requeues entries past stale threshold.
Usage:
  python scripts/queue_orchestrator/requeue_stale.py
  python scripts/queue_orchestrator/requeue_stale.py --dry-run
Authority: docs/PEARL_PRIME_ALWAYS_ON_POLICY.md, config/queue.yaml.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("requeue_stale")


def load_yaml(path: Path) -> dict:
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_redis():
    cfg = load_yaml(REPO_ROOT / "config" / "queue.yaml")
    url = os.environ.get("REDIS_URL") or cfg.get("redis_url", "redis://localhost:6379/0")
    try:
        import redis
    except ImportError:
        raise RuntimeError("redis required: pip install redis")
    return redis.from_url(url)


def main() -> int:
    ap = argparse.ArgumentParser(description="Requeue stale claimed jobs")
    ap.add_argument("--dry-run", action="store_true", help="Log only, do not LPUSH/HDEL")
    args = ap.parse_args()

    config_path = REPO_ROOT / "config" / "queue.yaml"
    if not config_path.exists():
        logger.error("Missing config/queue.yaml")
        return 1

    cfg = load_yaml(config_path)
    queue_name = cfg.get("queue_name", "pearl-jobs")
    processing_key = cfg.get("processing_key", "pearl-processing")
    stale_seconds = int(cfg.get("stale_seconds", 3600))

    try:
        r = get_redis()
    except Exception as e:
        logger.error("Redis connect failed: %s", e)
        return 1

    now = time.time()
    stale = []
    try:
        entries = r.hgetall(processing_key) or {}
    except Exception as e:
        logger.warning("HGETALL %s failed: %s", processing_key, e)
        return 0
    for job_id_b, val_b in entries.items():
        job_id = job_id_b.decode() if isinstance(job_id_b, bytes) else job_id_b
        try:
            data = json.loads(val_b.decode() if isinstance(val_b, bytes) else val_b)
        except (json.JSONDecodeError, TypeError):
            continue
        claimed_until = data.get("claimed_until") or 0
        if claimed_until < now:
            payload = data.get("payload") or data
            if isinstance(payload, dict):
                stale.append((job_id, json.dumps(payload)))
            else:
                stale.append((job_id, payload))
    if not stale:
        logger.info("no stale jobs")
        return 0
    logger.info("requeue %d stale jobs", len(stale))
    for job_id, payload in stale:
        if not args.dry_run:
            r.lpush(queue_name, payload)
            r.hdel(processing_key, job_id)
        logger.info("  requeued %s", job_id[:8] if len(job_id) >= 8 else job_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
