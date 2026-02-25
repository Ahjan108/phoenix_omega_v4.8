# Writer Spec: Markdown vs DOCX

**Purpose:** Clarify which file is authoritative, who uses which format, and how to keep section numbers in sync.  
**Audience:** Writers, dev, content ops.  
**Last updated:** 2026-02-25

---

## Which do writers use — markdown, docx, or both?

- **Markdown** (`specs/PHOENIX_V4_5_WRITER_SPEC.md`) is the **single source of truth**. All repo docs, checklists, and cross-references use the **markdown** and its section numbers (§1–§26, e.g. §5.5, §7, §12.2b, §13.6, §17, §19).
- **DOCX** (`specs/PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.docx`) exists as a **writer-facing export** for anyone who prefers Word (editing, comments, sharing outside the repo). In some workflows the docx has been used for delivery or validation.
- So: **both** are in use — markdown for repo authority and cross-refs, docx for writers who work in Word.

---

## Section numbering discrepancy

The markdown uses one numbering scheme (e.g. §5.5 BAND Cadence, §7 REFLECTION, §12.2b TIER_D, §13.6 Collision Guardrails, §17 Personas, §19 Collision Scan). If the docx was built by **editing a previous docx in place**, it can end up with a **different** scheme (e.g. §15.5, §18.1, §19.6, §16, §14). Same content, different “addresses.”

That matters when someone says “see §13.6” — in the docx that might be §19.6. Cross-references between spec, checklist, or comms then break for docx-only readers.

---

## Policy: keep section numbers in sync

1. **Authority:** The **markdown** is the only source of truth. Section numbers in the markdown are **authoritative** for all references (e.g. “see §13.6” means the markdown’s §13.6).
2. **If writers use the docx:** Regenerate the docx **from the markdown** (e.g. pandoc with a template that preserves Georgia font and your color scheme) so the docx is a true render of the markdown and section numbers match. Then writers can safely use either format for cross-references.
3. **If the docx is writer-only and refs are markdown-only:** You can treat numbering divergence as acceptable (different audiences). In that case, any spec note that says “see §13.6” should explicitly say “see §13.6 in the markdown spec” so docx users know to use the .md file for section lookups.

**Recommendation:** Regenerate the docx from markdown so the docx is always in sync and one set of section numbers works everywhere.

---

## Regenerating the docx from markdown

- Use **pandoc** (or your existing docx build script) with a reference.docx template that sets Georgia font, heading styles, and color scheme.
- After any change to `specs/PHOENIX_V4_5_WRITER_SPEC.md`, regenerate the docx and replace `specs/PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.docx` (or version the filename, e.g. v1.4).
- The repo does not currently automate docx generation; add a small script or CI step if you want it automatic.

---

## Summary

| Item | Role |
|------|------|
| **specs/PHOENIX_V4_5_WRITER_SPEC.md** | Single source of truth; authoritative section numbers (§1–§26). |
| **specs/PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.docx** | Writer-facing export; should be regenerated from markdown so section numbers match. |
| **Cross-references** | Always use markdown section numbers; if docx is regenerated from markdown, they match in both files. |
