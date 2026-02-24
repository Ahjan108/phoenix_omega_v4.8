# Seed mining pipeline

Pipeline to turn **human-authored source** (long-form copy, articles, notes) into **main-catalog atoms** for `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`.

This is separate from **teacher_mining** (KB → teacher_banks candidate/approved atoms). Seed mining targets the shared catalog.

## Design

1. **Input:** Raw document(s) — `.txt`, `.md`, or directory of files.
2. **Segment:** Split into chunks (by paragraph, section, or fixed word count). No LLM required; use double newlines or `max_chunk_words`.
3. **Role mapping:** Assign placeholder role (e.g. RECOGNITION) and BAND (e.g. 3). Optional rules: keyword-based role hints (e.g. "story of" → RECOGNITION, tension words → higher BAND).
4. **Output:** Write candidate blocks in CANONICAL block format (`## ROLE vNN` / `---` / metadata / `---` / prose / `---`).
5. **Validate:** Run `validate_canonical_atom_file()` (assembly_compiler) on the output. Optionally run `tools/tag_existing_atoms.py` to add narrative metadata.
6. **Repair:** On validation errors, either fix by hand or re-run with different chunking/role rules.
7. **Promote:** Move approved output into `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` (append or replace per workflow).

## Tools

- **seed_mine.py** — Minimal implementation: read file(s), chunk by paragraph or word count, assign RECOGNITION + BAND 3, write candidate CANONICAL-style file. Use `--out` to write to `get_these/` or a staging path for review.

## Usage

```bash
# Single file → candidate CANONICAL-style output
python -m tools.seed_mining.seed_mine --input draft.txt --persona nyc_executives --topic anxiety --engine overwhelm --out get_these/nyc_executives_anxiety_overwhelm_CANONICAL_candidate.txt

# Validate (after manual edits if needed)
python -c "
from pathlib import Path
from phoenix_v4.planning.assembly_compiler import validate_canonical_atom_file
p = Path('get_these/nyc_executives_anxiety_overwhelm_CANONICAL_candidate.txt')
print(validate_canonical_atom_file(p))
"
# Then tag narrative metadata and move to atoms/.../CANONICAL.txt when ready.
```

## Extensions (not implemented)

- Role classification (RECOGNITION vs MECHANISM_PROOF etc.) by keyword or model.
- BAND assignment by tension/cost keywords.
- Rewrite step (e.g. normalize second person, trim length).
- Automated repair loop (re-chunk on validation failure).
