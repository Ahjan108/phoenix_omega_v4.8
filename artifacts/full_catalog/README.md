# Full catalog artifacts

**US catalog (EN)** — `candidates_en/`  
- **120 BookSpecs** (plan-only). Default brand matrix: `stillness_press`, `cognitive_clarity`.  
- Regenerate:  
  `python3 scripts/generate_full_catalog.py --max-books 120 --plan-only --candidates-dir artifacts/full_catalog/candidates_en`  
- To compile (after content gates pass): drop `--plan-only`, add `--no-teacher-mode` to use shared atoms only, and set `--out-wave` as needed.

**Chinese catalog (ZH)** — `candidates_zh/`  
- **240 BookSpecs** (plan-only). Brand matrix: `config/catalog_planning/brand_teacher_matrix_zh.yaml` (24 brands × zh-TW/zh-HK/zh-CN/zh-SG). Locale group: `chinese_all`.  
- Regenerate:  
  `python3 scripts/generate_full_catalog.py --brand-matrix config/catalog_planning/brand_teacher_matrix_zh.yaml --locale-group chinese_all --max-books 240 --plan-only --candidates-dir artifacts/full_catalog/candidates_zh`  
- Compile requires `atoms/<locale>/` (e.g. `atoms/zh-TW/`) with persona/topic/engine structure; currently EN atoms only under `atoms/<persona>/`.

**Legacy / mixed** — `candidates/`  
- Previous run output (may include .spec.json and .json from earlier config).

---

## Why compile fails on full catalog (as of this run)

When running **without** `--plan-only`, every book hits the **tuple viability** gate before Stage 1:

1. **NO_STORY_POOL** — No or empty `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` for the arc’s engine (arc is chosen as first match for `persona__topic__*.yaml`).
2. **BAND_DEFICIT** — Story pool exists but doesn’t cover emotional bands required by the arc (e.g. missing band 1 or 5).
3. **TEACHER_EXERCISE_DEFICIT** — When using Teacher Mode (no `--no-teacher-mode`): teacher’s approved exercise count &lt; min (e.g. 5).
4. **No arc** — No master arc for (persona, topic), e.g. `shame` for several personas.

To get compiled plans: add/fill story pools and bands for the arc engines in use, add missing shame arcs, and either use `--no-teacher-mode` (shared atoms) or populate teacher banks so the exercise gate passes.
