#!/usr/bin/env python3
"""
Queue worker — pull jobs from Redis and run them. One heavy LM job per runner.
Run as long-lived process on self-hosted (or ubuntu for non-LM jobs).
Usage:
  python scripts/queue_orchestrator/worker.py
  python scripts/queue_orchestrator/worker.py --once
  python scripts/queue_orchestrator/worker.py --timeout 300
Authority: docs/PEARL_PRIME_ALWAYS_ON_POLICY.md, config/queue.yaml.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("queue_worker")

BLOCK_TIMEOUT = 30
MAX_RETRIES = 3


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


def _lm_studio_lock_module():
    for rel in ["scripts/lm_studio_lock.py"]:
        p = REPO_ROOT / rel.replace("/", os.sep)
        if p.exists():
            spec = importlib.util.spec_from_file_location("lm_studio_lock_mod", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def _build_argv(job: dict, defn: dict) -> list[str]:
    """Build command argv from job type definition and job params."""
    script = defn.get("script", "")
    template = list(defn.get("args_template") or [])
    params = job.get("params") or {}
    argv = []
    if script.startswith("python ") or " -m " in script:
        parts = script.split()
        argv.extend(parts)
    else:
        argv.append(sys.executable)
        argv.append(str(REPO_ROOT / script))
    i = 0
    while i < len(template):
        t = template[i]
        if t == "--date" and "date" in params:
            argv.append("--date")
            argv.append(params["date"])
        elif t == "--lane":
            argv.append("--lane")
            argv.append(str(params.get("lane", "en")))
            i += 2  # skip this and next (template value)
            continue
        elif t == "--cap":
            argv.append("--cap")
            argv.append(str(params.get("cap", 1)))
            i += 2
            continue
        else:
            argv.append(t)
        i += 1
    return argv


def run_job(job: dict, defn: dict) -> bool:
    """Run a single job. Returns True on success."""
    argv = _build_argv(job, defn)
    logger.info("run %s: %s", job.get("type"), " ".join(argv[-6:]))  # log last 6 args only
    try:
        r = subprocess.run(argv, cwd=REPO_ROOT, timeout=3600, capture_output=True, text=True)
        if r.returncode != 0:
            logger.warning("job %s exit %s: %s", job.get("id", "")[:8], r.returncode, (r.stderr or r.stdout or "")[:500])
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.warning("job %s timed out", job.get("id", "")[:8])
        return False
    except Exception as e:
        logger.warning("job %s error: %s", job.get("id", "")[:8], e)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl queue worker")
    ap.add_argument("--once", action="store_true", help="Process one job then exit")
    ap.add_argument("--timeout", type=int, default=0, help="Exit after this many seconds (0 = run forever)")
    args = ap.parse_args()

    config_path = REPO_ROOT / "config" / "queue.yaml"
    jobs_path = REPO_ROOT / "scripts" / "queue_orchestrator" / "jobs.yaml"
    if not config_path.exists() or not jobs_path.exists():
        logger.error("Missing config/queue.yaml or jobs.yaml")
        return 1

    cfg = load_yaml(config_path)
    spec = load_yaml(REPO_ROOT / cfg.get("jobs_spec", "scripts/queue_orchestrator/jobs.yaml"))
    job_types = spec.get("job_types") or {}
    queue_name = cfg.get("queue_name", "pearl-jobs")

    try:
        r = get_redis()
    except Exception as e:
        logger.error("Redis connect failed: %s", e)
        return 1

    lm_lock_mod = _lm_studio_lock_module()
    deadline = time.monotonic() + args.timeout if args.timeout else None
    processed = 0

    while True:
        if deadline and time.monotonic() >= deadline:
            logger.info("timeout reached; exiting")
            break
        raw = r.brpop(queue_name, timeout=min(BLOCK_TIMEOUT, args.timeout or BLOCK_TIMEOUT))
        if not raw:
            if args.once:
                break
            continue
        _, payload = raw
        try:
            job = json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("invalid job payload, skipping")
            continue
        jtype = job.get("type")
        defn = job_types.get(jtype)
        if not defn:
            logger.warning("unknown job type %s, skipping", jtype)
            continue
        retry = job.get("retry_count", 0)
        if retry >= MAX_RETRIES:
            logger.warning("job %s exceeded max retries, dropping", job.get("id", "")[:8])
            continue
        processing_key = cfg.get("processing_key", "pearl-processing")
        claim_timeout = int(cfg.get("claim_timeout_seconds", 3600))
        job_id = job.get("id", "")
        claim_data = {
            "payload": job,
            "claimed_until": int(time.time()) + claim_timeout,
            "worker_id": os.environ.get("RUNNER_NAME", "worker"),
        }
        r.hset(processing_key, job_id, json.dumps(claim_data))
        needs_lm = defn.get("needs_lm", False)
        ok = False
        try:
            if needs_lm and lm_lock_mod:
                try:
                    with lm_lock_mod.lm_studio_lock("queue-worker", shards=30, timeout_sec=180):
                        ok = run_job(job, defn)
                except Exception as e:
                    logger.warning("LM lock or run failed: %s", e)
            else:
                ok = run_job(job, defn)
        finally:
            r.hdel(processing_key, job_id)
        if not ok:
            job["retry_count"] = retry + 1
            r.lpush(queue_name, json.dumps(job))
            logger.info("requeued %s (retry %d)", job_id[:8] if len(job_id) >= 8 else job_id, job["retry_count"])
        else:
            processed += 1
        if args.once:
            break
    logger.info("processed %d jobs", processed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
