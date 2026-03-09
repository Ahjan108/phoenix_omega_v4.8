# Safe Push Guard

Blocks oversized pushes before upload to prevent long hanging pushes.

## Install

```bash
scripts/git/install_push_guard.sh /Users/ahjan/phoenix_omega /Users/ahjan/phoenix_omega/Qwen-Agent
```

This installs a `pre-push` hook and sets `core.hooksPath=.githooks` in each repo.

## Daily use

Normal `git push` now auto-runs the guard.

Optional wrapper with retry:

```bash
scripts/git/safe_push.sh origin main
```

## Default limits

- `PUSH_GUARD_MAX_COMMITS=30`
- `PUSH_GUARD_MAX_FILES=300`
- `PUSH_GUARD_MAX_TOTAL_MB=25`
- `PUSH_GUARD_MAX_SINGLE_MB=8`

If a push exceeds limits, it is blocked with a clear reason so you can split it into smaller pushes.
