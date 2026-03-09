# PR B: Qwen-Agent — disable cron, keep manual dispatch only

**Branch (in Qwen-Agent repo):** `codex/disable-prod-schedules`  
**Merge after:** PR A (phoenix_omega consolidation) is merged to main.

**Goal:** Remove all `schedule:` triggers from Qwen-Agent so it no longer runs production cron. Keep `workflow_dispatch` for manual/backup runs.

---

## 1. pearl_news_scheduled.yml

**Remove** the `schedule:` block. **Keep** `workflow_dispatch` and its `inputs`.

**Before (`on:` section):**
```yaml
on:
  schedule:
    # 3 runs per day, one per language:
    # 06:00 UTC → English, 10:00 UTC → Japanese, 14:00 UTC → Simplified Chinese
    - cron: '0 6 * * *'   # English
    - cron: '0 10 * * *'  # Japanese
    - cron: '0 14 * * *'  # Simplified Chinese
  workflow_dispatch:
    inputs:
      language:
        ...
```

**After:**
```yaml
on:
  workflow_dispatch:
    inputs:
      language:
        description: 'Language (en, ja, zh-cn, or all)'
        required: false
        default: 'en'
        type: choice
        options:
          - en
          - ja
          - zh-cn
          - all
```

---

## 2. audiobook_scheduled.yml

**Remove** the `schedule:` block. **Keep** `workflow_dispatch` and its `inputs`.

**Before (`on:` section):**
```yaml
on:
  schedule:
    - cron: '0 2 * * *'
    - cron: '0 14 * * *'
  workflow_dispatch:
    inputs:
      locale:
        ...
```

**After:**
```yaml
on:
  workflow_dispatch:
    inputs:
      locale:
        description: Locale for scheduled probe + comparator run
        required: false
        default: zh-TW
        type: choice
        options: [en-US, zh-TW, zh-HK, zh-SG, zh-CN, ja-JP, ko-KR]
```

---

## 3. runner_artifacts_cleanup.yml

**Remove** the `schedule:` block. **Keep** `workflow_dispatch` and its `inputs`.

**Before (`on:` section):**
```yaml
on:
  schedule:
    - cron: '30 3 * * *'
  workflow_dispatch:
    inputs:
      diag_keep_days:
        ...
```

**After:**
```yaml
on:
  workflow_dispatch:
    inputs:
      diag_keep_days:
        description: Keep runner diag logs newer than this many days
        required: false
        default: '14'
        type: string
      artifact_keep_days:
        description: Keep local artifacts newer than this many days
        required: false
        default: '14'
        type: string
```

---

## 4. No changes needed

- **locale_max_agents.yml** — already `workflow_dispatch` only (no schedule).
- **audiobook_manual.yml** — already `workflow_dispatch` only.
- **pearl_news_manual_expand.yml** — already `workflow_dispatch` only.
- **audiobook_regression.yml** — push/PR path-filtered + `workflow_dispatch`; no schedule. Leave as-is.

---

## Commands (run in Qwen-Agent repo)

```bash
cd /path/to/Qwen-Agent
git fetch origin
git checkout main
git pull --rebase origin main
git checkout -b codex/disable-prod-schedules
# Apply the three edits above (pearl_news_scheduled, audiobook_scheduled, runner_artifacts_cleanup)
git add .github/workflows/pearl_news_scheduled.yml .github/workflows/audiobook_scheduled.yml .github/workflows/runner_artifacts_cleanup.yml
git commit -m "chore(ci): disable production cron in Qwen-Agent; keep workflow_dispatch only

PR B of runtime consolidation. Production schedules run from phoenix_omega only.
- pearl_news_scheduled: remove schedule
- audiobook_scheduled: remove schedule
- runner_artifacts_cleanup: remove schedule"
git push -u origin codex/disable-prod-schedules
```

Then open a PR to `main` in Ahjan108/Qwen-Agent. Merge when ready.
