# Pearl Prime always-on policy

**Purpose:** Short policy for 24/7 Pearl Prime/v4 autonomy: queue-driven jobs, multi-runner readiness, SLA observability.

**Authority:** [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md). Implementation: [config/queue.yaml](../config/queue.yaml), [scripts/queue_orchestrator/](../scripts/queue_orchestrator/).

---

## Control plane vs workers

- **Phoenix (phoenix_omega)** = source of truth: specs, EI V2, recommender, catalog, marketing, video. Queue **master** runs here (publishes jobs to Redis).
- **Workers** pull jobs from the queue and run existing Phoenix scripts (ingest, recommender, catalog shard, EI learn, video distribution). Workers can run on self-hosted or ubuntu; LM-heavy jobs use one-heavy-job-per-runner and [Qwen-Agent LM lock](../Qwen-Agent/scripts/lm_studio_lock.py) when on self-hosted.

---

## Queue orchestration

- **Backend:** Redis. Set `REDIS_URL` (e.g. `redis://localhost:6379/0`). See [config/queue.yaml](../config/queue.yaml).
- **Queue master:** [scripts/queue_orchestrator/queue_master.py](../scripts/queue_orchestrator/queue_master.py). Run on schedule (e.g. [queue-master.yml](../.github/workflows/queue-master.yml) every 5 min) or `workflow_dispatch`. Publishes micro-batch jobs; does not run them.
- **Worker:** [scripts/queue_orchestrator/worker.py](../scripts/queue_orchestrator/worker.py). Long-lived process (or `--once` / `--timeout`). BRPOP job → claim in processing hash → run script → on success remove claim; on failure requeue with retry_count. LM jobs acquire LM Studio lock in same process.
- **Stale requeue:** [scripts/queue_orchestrator/requeue_stale.py](../scripts/queue_orchestrator/requeue_stale.py). Run on schedule; moves jobs in processing longer than `stale_seconds` back to the queue.

---

## Job types

Defined in [scripts/queue_orchestrator/jobs.yaml](../scripts/queue_orchestrator/jobs.yaml): `marketing-ingest`, `recommender-score`, `catalog-build-shard`, `ei-v2-learn`, `video-distribution`. Add or edit there; queue master and worker read the same spec.

---

## Multi-runner

- Keep current self-hosted runner as primary. Add a second runner for failover and workload split when ready.
- Same queue; both runners can run workers. One heavy LM job per runner (LM lock). Optional: job-type affinity per runner later.

---

## Observability

- **SLA summary:** [scripts/dashboard/queue_sla_dashboard.py](../scripts/dashboard/queue_sla_dashboard.py). Outputs queue depth, in-flight count, stale count. Run standalone or embed in a dashboard.
- **Secrets:** Queue master workflow needs `REDIS_URL` in repo/organization Secrets.

---

## Promotion gates

Unchanged: propose-only by default; auto-apply only when calibration + regression + safety gates pass. Queue-driven runs use the same gates.
