# Runtime consolidation — step-by-step

Follow these steps in order. You need: GitHub access to **Ahjan108/phoenix_omega_v4.8** and **Ahjan108/Qwen-Agent**, and a terminal in your phoenix_omega workspace.

---

## Part 1: Push branches and open PRs

### Step 1 — Push phoenix_omega consolidation branch

```bash
cd /Users/ahjan/phoenix_omega
git branch --show-current
# Should show: codex/runtime-consolidation

git push -u origin codex/runtime-consolidation
```

If push is rejected (e.g. "non-fast-forward"), run:
```bash
git fetch origin
git rebase origin/main
git push -u origin codex/runtime-consolidation
```

---

### Step 2 — Open PR A (phoenix_omega)

1. Go to **https://github.com/Ahjan108/phoenix_omega_v4.8**
2. You should see a banner: **"codex/runtime-consolidation had recent pushes"** → click **Compare & pull request**
3. If not: **Branches** → select `codex/runtime-consolidation` → **New pull request** (base: `main`)
4. **Title:** e.g. `Runtime consolidation: single production repo + governance + drift audit`
5. **Description:** Paste or link the summary:
   - Open [docs/PR_RUNTIME_CONSOLIDATION_SUMMARY.md](PR_RUNTIME_CONSOLIDATION_SUMMARY.md) in the repo and copy the contents, or
   - Write: "Consolidates Qwen runtime into phoenix_omega (allowlist only). Adds OWNERSHIP_MATRIX, drift-audit, removes legacy audiobook-regression.yml. See docs/PR_RUNTIME_CONSOLIDATION_SUMMARY.md"
6. Click **Create pull request**

---

### Step 3 — Push Qwen-Agent PR B branch

```bash
cd /Users/ahjan/phoenix_omega/Qwen-Agent
git branch --show-current
# Should show: codex/disable-prod-schedules

git push -u origin codex/disable-prod-schedules
```

If the remote doesn’t have this branch yet, the first push creates it. If push is rejected:

```bash
git fetch origin
git rebase origin/main
git push -u origin codex/disable-prod-schedules
```

---

### Step 4 — Open PR B (Qwen-Agent)

1. Go to **https://github.com/Ahjan108/Qwen-Agent**
2. **Compare & pull request** for `codex/disable-prod-schedules`, or **Branches** → `codex/disable-prod-schedules` → **New pull request** (base: `main`)
3. **Title:** e.g. `Disable production cron; keep workflow_dispatch only (PR B)`
4. **Description:** e.g. "Removes schedule triggers from pearl_news_scheduled, audiobook_scheduled, runner_artifacts_cleanup. Production cron runs from phoenix_omega only. Manual runs still work via workflow_dispatch."
5. **Create pull request**
6. **Do not merge yet** — merge PR B only after PR A is merged.

---

## Part 2: Before merging PR A — secrets and branch protection

### Step 5 — Add secrets in phoenix_omega (GitHub)

1. Go to **https://github.com/Ahjan108/phoenix_omega_v4.8** → **Settings** → **Secrets and variables** → **Actions**
2. Ensure these **repository secrets** exist (add any that are missing):
   - `WORDPRESS_SITE_URL`
   - `WORDPRESS_USERNAME`
   - `WORDPRESS_APP_PASSWORD`
   - `QWEN_BASE_URL`
   - `QWEN_API_KEY`
   - `QWEN_MODEL`
3. Values are the same ones you use in Qwen-Agent (no need to change them; just ensure phoenix_omega has them so migrated workflows can run).

---

### Step 6 — Check branch protection (phoenix_omega)

1. **Settings** → **Branches** → branch protection rule for `main`
2. Confirm **Required status checks** include at least:
   - Core tests  
   - Release gates  
   - EI V2 gates  
   - Change impact  
3. If not, add them so PR A (and future PRs) must pass these before merge.

---

## Part 3: Merge order

### Step 7 — Merge PR A first

1. In **phoenix_omega** PR A, wait until all required checks are green.
2. Click **Merge pull request** → confirm (squash or merge commit, per your preference).
3. Merge into `main`.

---

### Step 8 — Merge PR B second

1. Go to **Qwen-Agent** PR B.
2. Merge the PR into `main` so Qwen-Agent no longer runs production cron; only manual `workflow_dispatch` runs remain.

---

## Part 4: After merge

### Step 9 — Update local repos

**phoenix_omega:**
```bash
cd /Users/ahjan/phoenix_omega
git checkout main
git pull origin main
```

**Qwen-Agent:**
```bash
cd /Users/ahjan/phoenix_omega/Qwen-Agent
git checkout main
git pull origin main
```

---

### Step 10 — Self-hosted runner (if you use it)

- Workflows that need LM Studio (Pearl News, audiobook, locale_max_agents, catalog-book-pipeline, marketing-briefs) run on **self-hosted**.
- Ensure the runner is registered under **phoenix_omega_v4.8** (or the org) and is **running** when you want those jobs to execute.
- Same machine/runner you used for Qwen-Agent can be (re)registered for phoenix_omega if desired; see [docs/GITHUB_OPERATIONS_FRAMEWORK.md](GITHUB_OPERATIONS_FRAMEWORK.md).

---

## Quick reference

| Step | Where | Action |
|------|--------|--------|
| 1 | phoenix_omega terminal | `git push -u origin codex/runtime-consolidation` |
| 2 | GitHub phoenix_omega_v4.8 | Open PR A (codex/runtime-consolidation → main) |
| 3 | Qwen-Agent terminal | `git push -u origin codex/disable-prod-schedules` |
| 4 | GitHub Qwen-Agent | Open PR B (codex/disable-prod-schedules → main) |
| 5 | GitHub phoenix_omega Settings | Add 6 secrets if missing |
| 6 | GitHub phoenix_omega Settings → Branches | Confirm required checks on main |
| 7 | GitHub phoenix_omega | Merge PR A when green |
| 8 | GitHub Qwen-Agent | Merge PR B |
| 9 | Both repos | `git checkout main && git pull origin main` |
| 10 | Runner machine | Ensure self-hosted runner is running for phoenix_omega |

If any step fails (e.g. push rejected, checks red), stop and fix that step before continuing.
