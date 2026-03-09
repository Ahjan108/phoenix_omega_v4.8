# Release Velocity and Week-by-Week Schedule

**Purpose:** Legitimate-publisher velocity model and week-by-week scheduling. Schedule is **platform-safe**: the scheduler enforces caps from `safe_velocity.yaml` and **fails hard** if any brand/platform/week would exceed a platform's cap.

**Authority:** This doc and `config/release_velocity/`. Matrix caps in `brand_teacher_matrix.yaml` are **fail-safe guardrails** (restored); actual upload timing comes from the weekly schedule.

---

## Matrix caps (fail-safe, restored)

| Rule | Where | Role |
|------|--------|------|
| max_books_per_wave | brand_teacher_matrix.yaml `defaults` | Fail-safe cap per wave until scheduler is enforced everywhere |
| release_spacing_days | brand_teacher_matrix.yaml `defaults` | Interleaving / allocation; upload timing from schedule |
| max_books_per_brand_per_month | brand_teacher_matrix.yaml `defaults` | Must stay within strictest platform (e.g. Ximalaya 20–40/mo) |

Do not remove these: they protect against schedule output that exceeds platform-safe ranges.

---

## Target: 70–84/week is top-tier only (not default)

Research indicates some publishing houses run at **70–84 books per week**. That is a **long-term top-tier target for mature channels only**. Default scheduling **must** respect platform caps first (Google established 25–50/wk, Findaway 15–30/wk, Ximalaya 5–10/wk). The scheduler uses the **strictest** platform cap when generating the schedule and fails hard if any week would exceed any platform's cap.

---

## Ramp (start slow, build to target)

1. **Phase 1 — First 90 days:** Start with **1 series**. Build slowly so early weeks have few uploads; by day 90 the weekly rate is still conservative (e.g. ~10% of total catalog released in this phase).
2. **Phase 2 — Days 91–180 (6 months):** **30% growth** in weekly release rate. Steady increase; ~25% of catalog in this phase.
3. **Phase 3 — Next 60 days:** Ramp toward target with **staggered** week-to-week counts. Per-brand weekly count is **capped by the strictest platform** (e.g. Ximalaya 5–10/wk); remaining books released at that safe rate.

Config: `config/release_velocity/velocity_ramp.yaml`.

---

## Safe velocity (platform caps)

Do not exceed these when building or executing the weekly schedule. Stored in `config/release_velocity/safe_velocity.yaml`.

**Heuristics, not policy:** These caps are **internal guardrails** for schedule generation. They are not confirmed platform thresholds or guaranteed policy limits. Any "safe" weekly/monthly/yearly numbers (in this repo or cited elsewhere) are **operational heuristics** only. See [docs/CATALOG_ARCHITECTURE_AT_SCALE.md](./CATALOG_ARCHITECTURE_AT_SCALE.md) §9 (volume and catalog legitimacy).

| Platform | New imprint/account | Established |
|----------|----------------------|-------------|
| **Google Play Books** | 10–20/wk, 40–60/mo | 25–50/wk, 100–200/mo |
| **Findaway Voices** (Spotify / Apple / libraries) | 5–15/wk, 20–50/mo | 15–30/wk, 60–120/mo |
| **Ximalaya** (China) | 5–10/wk per verified account, 20–40/mo | Same; scaling needs verified entity, clean copyright, platform relationship |

Dumping 300 in one day or 200 audiobooks in one week = anomaly risk. Stagger uploads to stay within these ranges.

**Weekly pattern for 500–1,000 books/year (heuristic):** Many publishers releasing ~500–1,000 books/year use **8–20 books per week**, spread across multiple days, with **series clusters** (e.g. 5–8 series continuations, 2–4 new series starters) and **standalone discovery titles** (2–4). Rotate across imprints/brands. Treat as **operational guidance**, not platform guarantee. See [docs/CATALOG_ARCHITECTURE_AT_SCALE.md](./CATALOG_ARCHITECTURE_AT_SCALE.md) §12 (Angle Matrix) and §9 (operating playbook).

**Per-lane cap resolution:** Schedules are modeled as **two independent lanes** so EN is not throttled by Chinese/Ximalaya limits. Use `--lane` so caps apply only to that lane's platforms. See **Two independent lanes** below.

---

## Two independent lanes (EN vs ZH24)

Config: `config/release_velocity/lanes.yaml`. Caps are resolved **per lane**, not one global min.

| Lane | Scope | Platforms (cap against these only) |
|------|--------|-----------------------------------|
| **EN** | English brands; no Findaway coupling | `google_play_books` only (e.g. 10–20/wk new, 25–50/wk established). Chinese/Ximalaya limits do **not** apply. |
| **ZH24** | 24 Chinese brands (Findaway workflow) | Default: `findaway_voices` + `ximalaya`. Or sub-locale: `zh_cn` = local only (Ximalaya); `zh_tw_hk_sg` = Findaway-eligible (Findaway + Google for TW/HK/SG). |

- **Default (no `--lane`):** Global = all platforms; effective cap = min over Google, Findaway, Ximalaya (conservative; Ximalaya clamps).
- **`--lane en`:** Effective cap from Google only (e.g. 20/wk new imprint). Lets EN approach higher weekly rates without being limited by ZH.
- **`--lane zh24`:** Effective cap from Findaway + Ximalaya (or sub-locale). Apply conservative caps for this lane independently.
- **`--lane zh24 --zh-sublocale zh_cn`:** zh-CN only; local platforms (Ximalaya). Not Findaway/Google per locale_registry.
- **`--lane zh24 --zh-sublocale zh_tw_hk_sg`:** zh-TW / zh-HK / zh-SG; Findaway-eligible + Google for those storefronts.

Output JSON includes `lane`, `zh_sublocale` (if set), and `platforms` so the schedule is self-describing.

---

## Week-by-week schedule (what to upload when)

**Script:** `scripts/release/generate_weekly_schedule.py`

**Release topology (brand_days + same_day_cross_brand_max):** The script loads `config/release_velocity/release_scheduler.yaml` and enforces **reassign-first, fail-hard-second**. Each brand's books are assigned to weekdays only from that brand's `brand_days` list; no weekday may have more than `same_day_cross_brand_max` distinct brands. When a day would exceed the cap, overflow brands are moved to their next allowed day. The script fails with exit 1 only when no feasible assignment exists after reassignment (e.g. feasibility precheck: `7 * same_day_cross_brand_max >= brands_in_week` fails, or reassignment cannot converge). Schedule output includes a `day_assignments` map per week: `{ "mon": { "brand_id": [path, ...] }, ... }`.

**Input:** A wave file (one plan path per line) or a candidates directory of plan JSONs. Optional `--start-date` (YYYY-MM-DD); default is next Monday. Optional **`--lane en` | `--lane zh24`** for per-lane cap resolution; optional **`--zh-sublocale zh_cn` | `zh_tw_hk_sg`** when `--lane zh24`.

**Enforcement:** The script loads `safe_velocity.yaml` and (when `--lane` is set) `lanes.yaml`. Caps are applied only to that lane's platforms. It **fails hard** (exit 1) if any brand/platform/week would exceed that platform's `cap_max`.

**Output:** JSON or CSV.

- **Schedule:** `week`, `week_start`, `phase`, `brand_id`, `book_count`, `plan_paths` — which books to upload that week per brand.
- **Effective cap:** JSON includes top-level **`effective_platform_cap`** (the numeric cap used for schedule generation) so schedule consumers can read the cap basis directly without inferring from `platform_validation`. The printed summary also shows it (e.g. `effective_platform_cap=20`).
- **Platform validation (platform-aware columns):** `platform`, `trust_tier`, `cap_min`, `cap_max`, `scheduled_count`, `blocked_excess`. In JSON: under `platform_validation`. In CSV: second block in the same file. Use these to confirm each (week, brand, platform) is within safe range; `blocked_excess` is 0 when the schedule passes.

**Examples:**

```bash
# Global (conservative; all platforms; Ximalaya clamps)
python scripts/release/generate_weekly_schedule.py \
  --candidates-dir artifacts/full_catalog/candidates \
  --brand-from-plan --start-date 2026-03-01 --out artifacts/release_schedule.json

# EN lane: English brands only; Google cap (no Findaway/Ximalaya)
python scripts/release/generate_weekly_schedule.py --lane en \
  --candidates-dir artifacts/full_catalog/candidates \
  --brand-from-plan --start-date 2026-03-01 --out artifacts/release_schedule_en.json

# ZH24 lane: 24 Chinese brands (Findaway + Ximalaya)
python scripts/release/generate_weekly_schedule.py --lane zh24 \
  --candidates-dir artifacts/full_catalog/candidates \
  --brand-from-plan --start-date 2026-03-01 --out artifacts/release_schedule_zh24.json

# ZH24 sub-locale: zh-CN local only, or TW/HK/SG Findaway-eligible
python scripts/release/generate_weekly_schedule.py --lane zh24 --zh-sublocale zh_cn --out artifacts/release_schedule_zh_cn.json
python scripts/release/generate_weekly_schedule.py --lane zh24 --zh-sublocale zh_tw_hk_sg --out artifacts/release_schedule_zh_tw_hk_sg.json
```

---

## Brand matrix and planner

- **Brand matrix** (`config/catalog_planning/brand_teacher_matrix.yaml`): `defaults` include **fail-safe** `max_books_per_wave`, `release_spacing_days`, `max_books_per_brand_per_month`. Plus `teachers` and `teacher_constraints` (max_books_per_topic, max_books_per_persona) for **diversity**. Release timing comes from the weekly schedule; matrix caps are guardrails until scheduler enforcement is complete everywhere.
- **Teacher portfolio planner:** Allocates (teacher, topic, persona, brand) for catalog build. The `spacing_days` parameter is only for **interleaving** (avoid back-to-back same teacher in the allocation order), not for when to upload; upload timing comes from the weekly schedule.

---

## Scale: rollout by cohorts and per-author cap

**Do not assume safe by default at high throughput.** See **specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md §13** for the full stance on cross-account risk.

### Rollout by cohorts

- **Start with 1–3 brands** at target velocity (e.g. up to platform cap per account). Run the weekly schedule and uploads for that cohort only.
- **Monitor** rejection rates, Partner Center / dashboard alerts, and any quality or policy flags for at least 2–4 weeks.
- **Scale** to more brands only when signals are clean. Add brands in small cohorts (e.g. 2–3 at a time) and re-check signals after each expansion.
- Do not ramp all 24 brands to 25/week in parallel until cohort runs have shown stable, flag-free results.

### Same-day multi-account release bursts

- **Guard:** Avoid the platform seeing “many accounts release on the same day.” When building or executing the weekly schedule, **stagger release days by brand/cohort** (e.g. Mon: cohort A brands, Tue: cohort B, Wed: cohort C) so no single day has a large fraction of all brands releasing. This is one of the four network-level caps in **docs/CATALOG_ARCHITECTURE_AT_SCALE.md** (§5). Config: `config/release_velocity/release_scheduler.yaml` — `brand_days` (weekdays per brand), `same_day_cross_brand_max` (e.g. 3). Implement in process (runbook) and optionally in `generate_weekly_schedule.py`. Tie topology to editorial logic (programs/series), not pure randomness.

### Per-author / per-teacher cap (internal guard)

- **Operational guideline:** ≤ **50 titles per author/teacher per 90 days** per storefront account (from `docs/audiobook_ops_manual.md`). Same author name on > 50 titles in < 90 days is a stated spam signal.
- **At 100 books/month per brand:** To stay under 50/author/90 days you need at least **~6 authors/teachers** per brand (each ~17 books/month). With 2 authors, 50 each/month = 150 per 90 days each → above guideline; increase author/teacher count as volume rises.
- **Catalog-wide teacher share:** `config/catalog_planning/diversity_guards.yaml` → `max_share_per_teacher` (e.g. 8%) caps the fraction of any wave/allocation from a single teacher. Enforced in `generate_full_catalog` when using locale-group or brand-matrix.

---

## Summary

| What | Where |
|------|--------|
| Safe velocity (platform caps) | config/release_velocity/safe_velocity.yaml |
| Lanes (EN vs ZH24; per-lane platforms) | config/release_velocity/lanes.yaml |
| Ramp phases (90 d, 30% to 6 mo, 60 d toward target; capped by platform) | config/release_velocity/velocity_ramp.yaml |
| Generate week-by-week schedule | scripts/release/generate_weekly_schedule.py (`--lane en \| zh24`, `--zh-sublocale`) |
| Spec (velocity + schedule authority) | specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md §3, §7, §10 |
| Scale stance (cross-account risk, rollout by cohorts) | specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md §13; this doc § Scale |
| Per-author 90-day cap (≤50 titles/author/90 d) | docs/audiobook_ops_manual.md; this doc § Scale |
| Catalog-wide teacher-share cap | config/catalog_planning/diversity_guards.yaml → max_share_per_teacher |
| Same-day multi-account burst guard | This doc § Scale; config/release_velocity/release_scheduler.yaml (same_day_cross_brand_max) |
| Release wave scheduler (topology, brand_days, variability) | config/release_velocity/release_scheduler.yaml; docs/CATALOG_ARCHITECTURE_AT_SCALE.md §5b |
| Catalog architecture at scale (program, worldview, tiers, four caps) | docs/CATALOG_ARCHITECTURE_AT_SCALE.md |
| Volume/catalog legitimacy (heuristics only; low risk when diverse) | docs/CATALOG_ARCHITECTURE_AT_SCALE.md §9 |
| Series seeding and read-through (launch 2–3 books per series; cap new series starts per brand) | config/release_velocity/series_launch_policy.yaml; docs/CATALOG_ARCHITECTURE_AT_SCALE.md §13 |
