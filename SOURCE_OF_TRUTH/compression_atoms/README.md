# Compression Atoms (DEV SPEC 2 — slot_08_compression)

One short, high-recall distillation per chapter (40–120 words, exactly one insight). Used for memory anchor, snippets, shareability.

## Layout

- **approved/** — `approved/<persona_id>/<topic_id>/*.yaml` (one YAML per atom)
- **candidate/** — stubs for writer production before approval

## Atom YAML schema (per file)

```yaml
atom_id: "<persona>_<topic>_COMPRESSION_<n>"   # unique id
word_count: 72                                 # 40–120 (required)
compression_family: "C1"                       # optional; C1…C5 for diversity
body: "One reframe only. Short sentences..."   # 40–120 words; TTS-safe
```

## Rules (Writer Spec appendix)

- 40–120 words, 2–6 sentences
- No steps, no lists, no citations
- One reframe only; no cross-references
- TTS-safe (no em dashes; avoid long semicolons)

## Selection

Stage 3 selects deterministically from this pool when format includes COMPRESSION slot (e.g. F006). CI enforces word count and one-insight structure (no list/step patterns).
