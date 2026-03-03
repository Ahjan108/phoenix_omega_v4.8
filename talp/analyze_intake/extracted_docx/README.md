# Extracted .docx (Phase 1 gap closure)

Markdown extractions from .docx for Phase 1: diff against Writer Spec and merge unique TTS/emotional/somatic rules.

| File | Source .docx | Purpose |
|------|--------------|---------|
| **TTS_PROSE_GUIDE.md** | PHOENIX_V4_5_TTS_PROSE_GUIDE.docx | TTS prose rules; diff with Writer Spec §3, §12. |
| **EMOTIONAL_IMPACT_SPEC.md** | PHOENIX_V4_5_EMOTIONAL_IMPACT_SPEC.docx | Emotional impact rules; diff with Writer Spec §16 and phoenix_v4/qa/emotional_governance_rules.yaml. |
| **SOMATIC_WRITER_SPEC.md** | GOLDEN_PHOENIX_Writer_Spec_Somatic_V2.docx | Somatic writer guidance; merge any unique rules into Writer Spec. |

**Phase 1 (plan):** Extract → diff → document single source of truth per dimension → merge unique rules into Writer Spec; resolve conflicts.

**Single source of truth (after Phase 1 merge):**
- **TTS prose:** Writer Spec §3 (TTS Prose Law), §12 (formal gates), §12.2b (TTS reflection ceilings by tier). Extracted TTS_PROSE_GUIDE.md is reference only.
- **Emotional impact:** Writer Spec §16 + §16.8 (misfire tax, silence beat, never-know, integration modes, flinch audit). Machine rules: `phoenix_v4/qa/emotional_governance_rules.yaml`. Extracted EMOTIONAL_IMPACT_SPEC.md is reference only.
- **Somatic:** Writer Spec + optional somatic guidance; GOLDEN_PHOENIX extract is reference. No conflict with Writer Spec.

**Schema reconciliation (Canonical):** Single role schema = 5 roles (recognition, embodiment, pattern, mechanism_proof, agency_glimmer). Canonical story-atom path = `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`. See specs and SYSTEMS_DOCUMENTATION.

Extraction method: Python zipfile + word/document.xml (paragraph text only; no formatting).
