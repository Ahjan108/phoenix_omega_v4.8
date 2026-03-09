"""
Queue SLA — queue depth, processing (in-flight), stale count for Pearl Prime always-on.
Run standalone: python scripts/dashboard/queue_sla_dashboard.py
Or import get_queue_sla_summary(repo_root) for embedding in a dashboard.
Authority: docs/PEARL_PRIME_ALWAYS_ON_POLICY.md, config/queue.yaml.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_yaml(path: Path) -> dict:
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_queue_sla_summary(repo_root: Path | None = None) -> dict:
    """Return queue depth, in-flight count, stale count. Keys: queue_depth, in_flight, stale_count, ok."""
    root = repo_root or REPO_ROOT
    config_path = root / "config" / "queue.yaml"
    if not config_path.exists():
        return {"queue_depth": 0, "in_flight": 0, "stale_count": 0, "ok": False, "error": "no config"}
    cfg = load_yaml(config_path)
    queue_name = cfg.get("queue_name", "pearl-jobs")
    processing_key = cfg.get("processing_key", "pearl-processing")
    stale_seconds = int(cfg.get("stale_seconds", 3600))
    url = os.environ.get("REDIS_URL") or cfg.get("redis_url", "redis://localhost:6379/0")
    try:
        import redis
        r = redis.from_url(url)
    except Exception as e:
        return {"queue_depth": 0, "in_flight": 0, "stale_count": 0, "ok": False, "error": str(e)}
    try:
        depth = r.llen(queue_name)
        entries = r.hgetall(processing_key) or {}
        now = int(time.time())
        in_flight = len(entries)
        stale = 0
        for _k, v in entries.items():
            val = v.decode() if isinstance(v, bytes) else v
            try:
                data = json.loads(val)
                if (data.get("claimed_until") or 0) < now:
                    stale += 1
            except (json.JSONDecodeError, TypeError):
                pass
        return {
            "queue_depth": depth,
            "in_flight": in_flight,
            "stale_count": stale,
            "ok": True,
        }
    except Exception as e:
        return {"queue_depth": 0, "in_flight": 0, "stale_count": 0, "ok": False, "error": str(e)}


def main() -> int:
    summary = get_queue_sla_summary()
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
