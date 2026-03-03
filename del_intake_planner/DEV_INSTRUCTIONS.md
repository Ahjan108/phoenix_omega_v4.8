# ANGLE BLOCKER FIX — Dev Instructions
## Three patches to apply, in order

---

## THE PROBLEM

`BookSpec.angle_id` is `"default_angle"` in the main pipeline path.
This blocks the naming engine from generating specific titles.

**Root cause (two places):**
1. `catalog_planner.py` → `produce_single()` has no fallback when `series_id` is absent
2. `run_pipeline.py` → never passes `angle_id` to `produce_single`

---

## PATCH ORDER

### PATCH 1 — `config/catalog_planning/series_templates.yaml`
**File:** `series_templates_angles_patch.yaml`

Add `angles` arrays to every series that's missing them.
Use the angles defined in the patch file as canonical.

**Why first:** The planner derives angles from this config. Fix the data before fixing the code.

**Verify:**
```bash
python3 -c "
import yaml
with open('config/catalog_planning/series_templates.yaml') as f:
    cfg = yaml.safe_load(f)
series = cfg.get('series') or {}
missing = [k for k,v in series.items() if not v.get('angles')]
print('Series missing angles:', missing)
assert not missing, 'FAIL: patch incomplete'
print('PASS: all series have angles')
"
```

---

### PATCH 2 — `phoenix_v4/planning/catalog_planner.py`
**File:** `catalog_planner_angle_fix.py`

Two changes:

**A. Replace `produce_single` method** — add angle resolution order:
1. Caller-supplied angle_id (explicit override — unchanged)
2. Derived from series_id + series config (unchanged)
3. NEW: `_derive_angle(topic_id, persona_id, series_cfg)` — finds best-matched series by domain + persona affinity, returns first angle
4. Last resort: `f"{topic_id}_general"` (still better than "default_angle")

**B. Add two new methods:**
- `_derive_angle()` — persona-affinity-aware angle derivation
- `_topic_to_domain()` — inverse of existing `_domain_to_topic()`

**Verify:**
```bash
python3 -c "
from phoenix_v4.planning.catalog_planner import CatalogPlanner
c = CatalogPlanner()

# Test 1: produce_single without series
spec = c.produce_single(topic_id='relationship_anxiety', persona_id='nyc_exec')
assert spec.angle_id != 'default_angle', f'FAIL: got {spec.angle_id}'
print(f'PASS produce_single: angle_id = {spec.angle_id}')

# Test 2: produce_wave
specs = c.produce_wave(20, seed='test_seed')
defaults = [s for s in specs if s.angle_id == 'default_angle']
assert not defaults, f'FAIL: {len(defaults)} default_angle in wave'
print(f'PASS produce_wave: all {len(specs)} specs have real angles')
print('Angles:', set(s.angle_id for s in specs))
"
```

---

### PATCH 3 — `run_pipeline.py`
**File:** `run_pipeline_angle_fix.py`

Two changes:

**A. Add `--angle` CLI argument** (optional, default None)

**B. Pass `angle_id=args.angle` to `produce_single`**
- When `--angle` is passed: explicit override, exact angle used
- When not passed: `_derive_angle()` runs automatically (from Patch 2)

**C. Add UserWarning** if resolved angle ends with `_general`
(signals to operator that a more specific angle is available via `--series` or `--angle`)

**Verify:**
```bash
# Test with no angle flag — should derive, not default
python3 run_pipeline.py --topic relationship_anxiety --persona nyc_exec
# Expected: no "default_angle" in output, possible UserWarning if _general

# Test with explicit angle
python3 run_pipeline.py --topic relationship_anxiety --persona nyc_exec --angle at_work
# Expected: angle_id = "at_work", no warning

# Test with series (existing path, should still work)
python3 run_pipeline.py --topic relationship_anxiety --persona nyc_exec --series social_anxiety_arc
# Expected: angle_id = first angle from series config
```

---

## AFTER ALL PATCHES

Run full verification:
```bash
python3 -c "
from phoenix_v4.planning.catalog_planner import CatalogPlanner
c = CatalogPlanner()
specs = c.produce_wave(50, seed='verification_seed')
defaults = [s for s in specs if s.angle_id == 'default_angle']
generals = [s for s in specs if s.angle_id.endswith('_general')]
print(f'Total: {len(specs)}')
print(f'default_angle: {len(defaults)} — must be 0')
print(f'_general fallback: {len(generals)} — should be 0 if series_templates complete')
print(f'Real angles: {len(specs) - len(defaults) - len(generals)}')
"
```

Both `default_angle` and `_general` counts should be 0 after all three patches.
If `_general` count > 0, there are topics/personas with no matching series in config.
Those are the next series to add to `series_templates.yaml`.

---

## WHAT THIS UNBLOCKS

Once angle_id is real:
- Naming engine can generate specific titles (not "Anxiety Book 1")
- `title_stems.yaml` scenario_variants can be used
- `subtitle_patterns.yaml` brand preferences apply correctly
- Marketing metadata layer has meaningful angle context
- Hook bank generation has real angle to pull from

This is the last config blocker before naming engine code can be written.
