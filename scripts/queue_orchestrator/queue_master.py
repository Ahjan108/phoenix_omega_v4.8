#!/usr/bin/env python3
"""
Queue master — publish micro-batch jobs to Redis for Pearl Prime always-on workers.
Run on schedule (e.g. every 1–5 min) or workflow_dispatch. Does not run jobs; workers pull and run.
Usage:
  python scripts/queue_orchestrator/queue_master.py
  python scripts/queue_orchestrator/queue_master.py --types marketing-ingest,ei-v2-learn
  python scripts/queue_orchestrator/queue_master.py --dry-run
Authority: docs/PEARL_PRIME_ALWAYS_ON_POLICY.md, config/queue.yaml.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("queue_master")


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
        raise RuntimeError("redis required for queue: pip install redis")
    return redis.from_url(url)


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish Pearl jobs to Redis")
    ap.add_argument("--types", default="", help="Comma-separated job types to publish (default: all that have shards or single run)")
    ap.add_argument("--dry-run", action="store_true", help="Log only, do not LPUSH")
    args = ap.parse_args()

    config_path = REPO_ROOT / "config" / "queue.yaml"
    jobs_path = REPO_ROOT / "scripts" / "queue_orchestrator" / "jobs.yaml"
    if not config_path.exists() or not jobs_path.exists():
        logger.error("Missing config/queue.yaml or scripts/queue_orchestrator/jobs.yaml")
        return 1

    cfg = load_yaml(config_path)
    jobs_spec_path = REPO_ROOT / cfg.get("jobs_spec", "scripts/queue_orchestrator/jobs.yaml")
    spec = load_yaml(jobs_spec_path)
    job_types = spec.get("job_types") or {}

    queue_name = cfg.get("queue_name", "pearl-jobs")
    types_filter = [t.strip() for t in args.types.split(",") if t.strip()] if args.types else None

    now = datetime.now(timezone.utc).isoformat()
    batch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    published = 0

    try:
        r = get_redis()
    except Exception as e:
        logger.error("Redis connect failed: %s", e)
        return 1

    for jtype, defn in job_types.items():
        if types_filter and jtype not in types_filter:
            continue
        priority = defn.get("priority", 5)
        shards = defn.get("shards") or []
        if not shards:
            shards = [None]
        for shard in shards:
            params = {}
            if defn.get("args_template"):
                if "--date" in defn["args_template"]:
                    params["date"] = batch_date
                if shard:
                    params["lane"] = shard
            payload = {
                "id": str(uuid.uuid4()),
                "type": jtype,
                "shard": shard,
                "priority": priority,
                "created_ts": now,
                "params": params,
                "retry_count": 0,
            }
            if not args.dry_run:
                r.lpush(queue_name, json.dumps(payload))
            logger.info("  publish %s shard=%s id=%s", jtype, shard, payload["id"][:8])
            published += 1

    logger.info("Published %d jobs to %s", published, queue_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
