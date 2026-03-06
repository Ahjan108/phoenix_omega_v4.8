#!/usr/bin/env python3
"""
Translate atoms for all configured locales (cloud/Qwen matrix).
Stub: implement when translation pipeline is ready.
See config/localization/content_roots_by_locale.yaml and docs/DOCS_INDEX.md § Translation.

WHEN IMPLEMENTING — key content changes to handle (added 2026-03-06):
  1. New atom slot types: PIVOT, TAKEAWAY, THREAD, PERMISSION
     - PIVOT and THREAD are short (2-3 sentences / 1-2 sentences). Translate whole.
     - TAKEAWAY is a single thesis sentence derived from arc chapter_thesis[ch]. Translate that
       sentence from CHAPTER_THESIS_BANK (docs/CHAPTER_THESIS_BANK.md) for each locale.
     - PERMISSION is 2-4 sentences, second-person, chapter-specific. Needs cultural review
       per locale — direct permission language varies significantly across cultures.
  2. chapter_thesis field in arc YAML (config/source_of_truth/master_arcs/*.yaml)
     - 20 thesis sentences per arc, one per chapter.
     - Translate along with atom content; TAKEAWAY slot text = translated chapter_thesis[ch].
  3. Bestseller structure labels (docs/BESTSELLER_STRUCTURES.md) are internal planning metadata;
     structure names do not appear in rendered audio. No translation required for structure IDs.
  4. CHAPTER_THESIS_BANK (docs/CHAPTER_THESIS_BANK.md): translate the thesis sentences per engine
     type × locale. These feed the TAKEAWAY slot.
  5. Glossary (config/localization/quality_contracts/glossary.yaml): when implementing, add
     PIVOT/TAKEAWAY/THREAD/PERMISSION slot type names as internal terms (not translated — they
     are pipeline IDs). Do add canonical translations for key brand terms used in thesis sentences
     (e.g. "nervous system", "alarm", "mask", "the pattern") per locale.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("Stub: translate_atoms_all_locales_cloud not yet implemented.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
