# Writer Dev Spec — Phase 2: Coverage-Aligned Inventory Expansion

Operational spec for dev team building writer tooling. No ambiguity. No philosophy. Pure operational spec.

---

## 0. Purpose

Now that:

- Plan Compiler is deterministic
- Slot resolution works for all types
- No-reuse enforced
- Capability check implemented
- Strict mode blocks placeholders

The writer is no longer producing prose casually. The writer is producing **structured inventory that satisfies compiler math.**

This spec defines:

- What metrics dev must expose
- What writer must produce
- What the system must validate

---

## 1. Coverage Dashboard (Dev Tooling Required)

Dev must implement:

```bash
python scripts/coverage_report.py --persona P --topic T --format F
```

Output must include:

### A. Slot Pool Counts

Per slot type:

| Slot Type | Pool Size | Required for N Chapters | Achievable Chapters |
|-----------|-----------|-------------------------|---------------------|

Where:

- **Required** = `requested_chapters * slots_per_chapter`
- **Achievable** = `floor(pool_size / slots_per_chapter)`

### B. STORY Band Distribution

| Band | Count |
|------|-------|
| 1 | X |
| 2 | X |
| 3 | X |
| 4 | X |
| 5 | X |

And: % per band, distinct bands count.

### C. INTEGRATION Mode Distribution

| Mode | Count |
|------|-------|
| BODY-LANDED | |
| COST-VISIBLE | |
| QUESTION-OPEN | |
| FMT | |
| STILL-HERE | |
| SOMEONE-ELSE | |

**Flags:**

- If STILL-HERE count == 0
- If STILL-HERE count > 3
- If any mode > 50% of pool

### D. HOOK Type Distribution

| Type | Count |
|------|-------|
| sensory_image | |
| context_drop | |
| direct_address | |
| imagery_hook | |
| recognition_beat | |

**Flags:**

- Any type > 40%
- Any type < 2

### E. SCENE Token Coverage

List:

- Unique tokens used
- Tokens never used
- Tokens used in > 50% of scenes

---

## 2. Writer Production Rules (What Dev Must Enforce)

Writer must:

| Rule | Description |
|------|-------------|
| ✔ Only write atoms for red coverage deficits | No random additions |
| ✔ Maintain no-reuse viability | New atoms must increase achievable chapters |
| ✔ Expand emotional diversity | If band coverage is skewed, add missing bands |
| ✔ Maintain slot type balance | No overproducing HOOKS while SCENES are low |

---

## 3. STORY Band Targets (Minimum Healthy Distribution)

For 8-chapter format target, minimum healthy pool:

| Band | Min Count |
|------|-----------|
| 1 | ≥ 2 |
| 2 | ≥ 3 |
| 3 | ≥ 4 |
| 4 | ≥ 3 |
| 5 | ≥ 2 |

Ensures emotional curve validator can succeed. Dev should not enforce rigidly — **print warnings if skewed**.

---

## 4. Integration Mode Health Targets

Target pool health:

| Mode | Min Count |
|------|-----------|
| BODY-LANDED | ≥ 2 |
| COST-VISIBLE | ≥ 2 |
| QUESTION-OPEN | ≥ 2 |
| FMT | ≥ 2 |
| STILL-HERE | ≥ 1 |
| SOMEONE-ELSE | ≥ 1 |

**Enforced rule:** STILL-HERE max 1 per book (resolver level).

---

## 5. Exercise Framing Expansion

Dev must provide:

```bash
python scripts/exercise_coverage.py
```

Output:

| Exercise Name | Framings Count | Band Ranges Covered |
|---------------|----------------|---------------------|

Writer must ensure each exercise has framings for:

- Low-band (1–2)
- Mid-band (3–4)
- High-band (4–5)

No new exercise scripts required yet. Only framing diversity.

---

## 6. Strict Compile Loop (Dev Required)

Dev must provide:

```bash
python scripts/compile_strict.py
```

Behavior:

1. `capability_check(strict)`
2. `compile_plan(require_full_resolution=True)`
3. `validate_compiled_plan()`
4. `render_plan_to_txt(strict=True)`

Exit non-zero if any failure. Writer uses this to verify readiness.

---

## 7. Writer Stop Condition

Writer stops when:

- `capability_check(strict)` passes
- `compile_plan(require_full_resolution=True)` passes
- `validate_compiled_plan` passes
- Emotional curve validator passes
- No slot type flagged red in coverage report

At that point: **Inventory is sufficient. Book is mathematically fillable.**

---

## 8. What Writer Must NOT Do

Dev must document:

Writer should NOT:

- Rewrite approved atoms during coverage phase
- Add reuse logic
- Add band metadata incorrectly
- Add random hooks/scenes "for style"
- Modify slot structure

**Structure is frozen. Inventory is expandable.**

---

## 9. Optional Advanced Tooling (Phase 3)

After first book ships:

- Golden snapshot test
- Determinism regression test
- Pool exhaustion simulator
- Multi-run emotional curve sampler

Not required now.

---

## 10. Deliverables for Dev Team

Dev must implement:

| Deliverable | Purpose |
|-------------|---------|
| `scripts/coverage_report.py` | Persona × topic × format coverage; slot pools, STORY bands, INTEGRATION modes, HOOK types, SCENE tokens |
| `scripts/exercise_coverage.py` | Exercise framings by band range |
| `scripts/compile_strict.py` | Strict compile loop (capability → compile → validate → render) |
| Integration of strict mode into CI | Block release if strict compile fails |

---

## Summary

The writer is no longer writing chapters. The writer is:

> Supplying structured inventory to satisfy deterministic compiler math.

When coverage is green, the system becomes generative.
