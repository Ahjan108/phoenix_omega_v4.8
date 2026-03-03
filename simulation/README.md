# Phoenix V4.5 Format Simulation

Tests **all varieties of configuration** from [PHOENIX_V4_5_COMPLETE_FORMAT_SPEC.docx](../PHOENIX_V4_5_COMPLETE_FORMAT_SPEC.docx): 14 formats, 6 tiers (S A B C D E), from 90-second resets to 6-hour deep books.

No real atoms or plan compiler — **mock pool** and **structural validation** only. Use to:

- Confirm every format/tier gets exercised
- Find validation gaps (missing rules, wrong thresholds)
- Run 10 → analyze → fix/enhance → repeat to 1k books

## Quick run

```bash
cd simulation
python run_simulation.py --n 10 --analyze
# Monte Carlo CTSS duplication-risk (vs index; run after building candidate pool)
# python run_monte_carlo_ctss.py --candidates-dir ../artifacts/candidates --n 1000 --out ../artifacts/simulation/ctss_monte_carlo.json
python run_simulation.py --n 100
python run_simulation.py --n 1000 --out ../artifacts/simulation_1k.json
# With Phase 2 (waveform, arc, drift)
python run_simulation.py --n 1000 --phase2 --out ../artifacts/simulation_1k_phase2.json
# With Phase 2 + Phase 3 (content/emotional force)
python run_simulation.py --n 1000 --phase2 --phase3 --out ../artifacts/simulation_1k_phase3.json
```

## Config

- **config/v4_5_formats.yaml** — 14 formats (duration, words, chapters, parts, tier)
- **config/validation_matrix.yaml** — V4.5 rules per tier (misfire tax, silence beat, never-know, interrupt, flinch audit, reflection ceiling, **volatility quotas by tier**, etc.)
- **config/emotional_temperature_curves.yaml** — Per-format temperature sequences (cool/warm/hot/land) and requirements (volatility spikes, rupture, action-despite-pattern, landing)

Optional: `pip install pyyaml` to load YAML from disk; otherwise simulator uses built-in fallback config.

## Workflow: run 10, analyze, fix, enhance, repeat to 1k

1. **Run 10**  
   `python run_simulation.py --n 10 --analyze`  
   Ensures at least one book per format (14), so all config varieties are hit.

2. **Analyze**  
   Check "By format", "By tier", "Error reasons". Any failure = missing or wrong rule or threshold.

3. **Fix / enhance**  
   - Adjust **validation_matrix.yaml** (or fallback in `simulator.py`) for wrong mins/maxs.  
   - Add missing rules (e.g. cost chapter, temperature curve) in `validate_plan()`.  
   - Increase mock **pool_per_type** if failures are capability only.

4. **Repeat**  
   Re-run 10 until pass_rate 100%. Then scale:

   - `--n 100`  
   - `--n 1000`  
   - Optionally `--out artifacts/simulation_1k.json` for records.

## Phase 2 (emotional waveform, arc, drift)

Use `--phase2` to run the second layer after Phase 1:

- **Waveform:** intensity variance, volatile chapters, silence density, no long flat run.
- **Arc:** primary character ≥3 appearances, consequence/action present, interrupt placement.
- **Drift:** stacks of 10 books checked for metaphor/ending phrase overlap (synthetic IDs).

Phase 2 uses **synthetic metadata** (no real atoms). It validates that the pipeline and gates exist; real atom metadata would feed the same checks. See [SIMULATION_PHASE2_SCOPE.md](SIMULATION_PHASE2_SCOPE.md).

## Phase 3 (content / emotional force) — MVP

Use `--phase3` to run content-aware validation on (synthetic) chapter text:

- **Volatility reality:** Volatile chapters must have ≥3 escalation verbs, ≥2 sensory stress words, ≥1 reaction marker.
- **Cognitive balance:** cognitive verbs / body words ≤ 5 (fail) or ≤ 3 (warn).
- **Consequence authenticity:** If action verbs present, reaction markers must appear in chapter.
- **Reassurance repetition:** Across stacks of 20 books, no phrase in >60% (fail) or >40% (warn).

Phase 3 runs on **synthetic** chapter text in simulation (~12% of books get “flat” text and fail). With real assembled output, pass the same chapter text and run `validate_book_phase3(chapters)` then stack-wise `check_reassurance_repetition`. See [phase3_mvp.py](phase3_mvp.py) and [PHASE3_MVP.md](PHASE3_MVP.md).

## Exit code

- 0 if all simulated books passed Phase 1 and (when `--phase2`) Phase 2 and drift and (when `--phase3`) Phase 3.
- 1 if any failed (and analysis is printed when `--analyze` or when there are failures).
