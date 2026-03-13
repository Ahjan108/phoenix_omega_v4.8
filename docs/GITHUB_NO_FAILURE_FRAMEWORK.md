# GitHub No-Failure Framework

**Purpose:** Operational standard for preventing GitHub Action hangs, runner dropouts, and long failed cycles across `phoenix_omega_v4.8` and `Qwen-Agent`.

**Primary companion docs:** [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md) (workflow matrix, concurrency, LM lock), [RUNNER_TRIAGE_ONE_PAGER.md](../Qwen-Agent/docs/RUNNER_TRIAGE_ONE_PAGER.md) (Qwen-Agent runner triage), [GO_LIVE_FINAL_CHECKLIST.md](./GO_LIVE_FINAL_CHECKLIST.md) (go-live evidence). Qwen-Agent copy: [Qwen-Agent/docs/GO_LIVE_FINAL_CHECKLIST.md](../Qwen-Agent/docs/GO_LIVE_FINAL_CHECKLIST.md).

---

## 1) Non-negotiable rules

1. One runner = one heavy queue.
2. Heavy jobs must be sharded (never one giant monolithic run).
3. Every heavy workflow must include preflight + warmup + timeout + retry.
4. LM Studio calls for production pipelines must disable thinking mode.
5. Never overlap heavy classes outside their assigned UTC windows.
6. No production sign-off without run URLs + artifacts + digest evidence.

---

## 2) Two-repo reliability model

- `phoenix_omega_v4.8`: system source of truth, CI gates, release workflows.
- `Qwen-Agent`: self-hosted runtime for Pearl News, audiobook, localization.
- Rule: reliability hardening for LM workloads lives where the workload runs (Qwen-Agent workflows + runner scripts).

---

## 3) Job classes and scheduling policy

### Heavy classes

- Audiobook full-golden regression
- Audiobook scheduled comparator run
- Locale translation batches (`translate+validate`)
- Pearl News expand jobs

### Policy

- Use workflow `concurrency` plus LM lock. Lock lives in **Qwen-Agent:** [scripts/lm_studio_lock.py](../Qwen-Agent/scripts/lm_studio_lock.py) (three-tier light/medium/heavy, stale recovery). See [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md) for which workflows use it.
- Enforce UTC windows via **Qwen-Agent** [scripts/runner/heavy_window_guard.py](../Qwen-Agent/scripts/runner/heavy_window_guard.py) and [config/runner/heavy_windows.yaml](../Qwen-Agent/config/runner/heavy_windows.yaml).
- Validate-only and smoke runs are allowed as light jobs.
- **Phoenix workflows on self-hosted** (e.g. catalog-book-pipeline, marketing-briefs-and-proposals when run on self-hosted) must use the same concurrency + LM lock pattern so they do not collide with Qwen-Agent heavy jobs.

---

## 4) Required workflow hardening pattern

Every heavy self-hosted workflow must include:

1. `timeout-minutes` at job level.
2. `concurrency` group.
3. Dependency install step.
4. LM preflight:
   - `/v1/models` health check
   - warmup completion call (JSON parse checked)
5. Runner health checks:
   - free memory floor
   - free disk floor
6. Attempt loop (retry once) for heavy command.
7. Artifact upload on completion/failure.
8. Lock lifecycle correctness:
   - Acquire LM lock in the same step/process that executes the heavy command.
   - Do not acquire lock in one workflow step and run heavy work in a later step.

---

## 5) LM Studio request policy (critical)

For production draft/judge/translation calls:

- Set `enable_thinking: false`.
- Use deterministic low-temp for judge/validation paths.
- Keep warmup call explicit and meaningful (not tiny no-op).
- Warmup success criteria:
  - parseable JSON response
  - no `error` field
  - non-empty assistant output/content

Why:

- Prevent `<think>` token waste.
- Reduce timeout/disconnect risk.
- Improve throughput stability under runner load.

---

## 6) Sharding standards

### Audiobook regression

- Full-golden must run locale shards (matrix), not one 24-sample monolith.
- Smoke run remains fast health gate.
- Target shard SLO: each heavy shard should complete within 45 minutes; if not, split further.

### Localization

- Shard at teacher/topic granularity (one LLM call unit per shard).
- Use bounded `max_agents` defaults (`1–2` safe baseline).
- Include heartbeat logs and consecutive-failure early abort.

### Pearl News

- Scheduled path favors reliability; manual expand path used for heavy expansion.

---

## 7) Runner reliability controls

Required controls on self-hosted machine:

1. Runner service installed and monitored.
2. Watchdog LaunchAgent active:
   - auto-restart runner if down
   - monitor broker timeout spikes
3. Cleanup automation:
   - prune old `_diag` logs
   - prune aged local artifacts
4. Triage runbook available with exact recovery commands.

---

## 8) Git push reliability controls

To prevent long push hangs and oversized uploads:

1. Install pre-push guard (`scripts/git/push_guard.py`) in both repos.
2. Block pushes that exceed configured payload thresholds.
3. Use guarded wrapper (`scripts/git/safe_push.sh`) for retry on transient network errors.
4. Split large changes before push instead of retrying giant uploads.

---

## 9) Model artifact strategy (NO Hugging Face)

Policy: Keep GitHub repos for code/config only. Do not store model binaries in git history.

Allowed pattern:

1. Store model binaries (`.gguf`, `.bin`, large checkpoints) in a non-git artifact store
   (private object storage, NAS, internal registry, or cloud bucket).
2. Keep a small manifest in repo with:
   - variant name
   - download URL/path
   - SHA256
   - expected size
3. Download on runner via scripted preflight only when missing.
4. Verify SHA256 before use.
5. Cache locally on runner to avoid repeated downloads.

Repository guardrails:

- `.gitignore` must exclude model binaries.
- Pre-push guard must block model extensions and oversized files before upload.
- CI should fail fast if manifest is missing required checksum fields.

This avoids push-time hangs and keeps git operations deterministic.

---

## 10) Known anti-patterns (must avoid)

1. Lock acquired in one workflow step and used in later steps (lock is lost between steps).
2. Warmup calls with too few tokens / no parse check.
3. Heavy job without matrix/shards.
4. Running manual heavy workflows concurrently during scheduled heavy windows.
5. Marking readiness from smoke-only evidence.
6. Committing model binaries (`.gguf`, `.bin`) into GitHub repos.
7. Allowing any self-hosted Phoenix workflow to run heavy LM work without the same lock/window policy used in Qwen-Agent.

---

## 11) Operational evidence standard

For each production-hardening claim, store:

1. Workflow run URL
2. Commit SHA
3. Artifact name + digest
4. Queue/manual review status
5. Model ID used

No “100% ready” declaration without all five.

---

## 12) Implementation status baseline (current)

Implemented:

- LM lock (three-tier light/medium/heavy, compatibility matrix) + stale-lock recovery (dead pid + TTL); configurable thresholds via env (see [Qwen-Agent/scripts/lm_studio_lock.py](../Qwen-Agent/scripts/lm_studio_lock.py))
- Heavy window guard + config (Qwen-Agent)
- Runner watchdog + cleanup workflow
- Warmup and preflight in heavy Qwen-Agent workflows
- Warmup/preflight/retry hardening in self-hosted Phoenix workflows: `marketing_continuous.yml`, `marketing-briefs-and-proposals.yml`, `catalog-book-pipeline.yml`
- Sharded audiobook regression; locale batches sharded by teacher/topic with heartbeat and per-topic timeout
- Push guard and safe push wrapper (phoenix_omega [scripts/git/](../scripts/git/), installable in both repos)

Still enforce continuously:

- Keep workflow edits aligned to this framework.
- Re-audit self-hosted workflows whenever new heavy jobs are added.
