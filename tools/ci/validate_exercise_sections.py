"""CI: validate exercise sections (post-overlay). Run from repo root."""
from __future__ import annotations

import sys
import yaml
from pathlib import Path

# Paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
EXERCISES_DIR = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "approved"
OVERLAYS_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "persona_overlays.yaml"

try:
    from phoenix_v4.exercises.overlay_substitution import (
        apply_persona_overlay,
        validate_callout_prefix,
        validate_required_terms_for_aha,
        validate_banned_outcomes,
    )
except ImportError:
    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.exercises.overlay_substitution import (
        apply_persona_overlay,
        validate_callout_prefix,
        validate_required_terms_for_aha,
        validate_banned_outcomes,
    )


def _load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def _word_count(s: str) -> int:
    return len([w for w in (s or "").split() if w.strip()])


def _validate_section(section_name: str, text: str, min_words: int, max_words: int | None, require_aha_terms: bool = False):
    errs = []
    if not (text and text.strip()):
        errs.append(f"{section_name} is empty")
        return errs
    wc = _word_count(text)
    if wc < min_words:
        errs.append(f"{section_name} word_count {wc} < min_words {min_words}")
    if max_words is not None and wc > max_words:
        errs.append(f"{section_name} word_count {wc} > max_words {max_words}")
    errs.extend(validate_callout_prefix(section_name, text))
    errs.extend(validate_banned_outcomes(text))
    if require_aha_terms:
        errs.extend(validate_required_terms_for_aha(text))
    lower = (text or "").lower()
    if "performance pressure may be chemical" in lower:
        errs.append("warn: overlay collision phrase detected")
    return errs


def main() -> int:
    if not EXERCISES_DIR.exists():
        print("OK: no approved exercises dir")
        return 0
    overlays = _load_yaml(OVERLAYS_PATH)
    persona_overlays = overlays.get("persona_overlays", {})
    apply_to_sections = overlays.get("apply_to_sections", ["aha_noticing"])
    phrase_map = {p: cfg.get("lexical_shift", {}) for p, cfg in persona_overlays.items()}
    token_overlays = overlays.get("token_overlays", {})
    failures = []
    for ex_file in EXERCISES_DIR.rglob("*.yaml"):
        ex = _load_yaml(ex_file)
        content = ex.get("content", {})
        required = ("intro", "guided_practice", "aha_noticing", "integration")
        if not all(sec in content for sec in required):
            for sec in required:
                if sec not in content:
                    failures.append((str(ex_file), sec, "missing section"))
            continue
        for persona in phrase_map:
            rendered = apply_persona_overlay(
                dict(content), persona, apply_to_sections,
                token_overlays=token_overlays, phrase_overlays=phrase_map,
            )
            for err in _validate_section("aha_noticing", rendered.get("aha_noticing", ""), 40, 150, require_aha_terms=True):
                if "missing required callout prefix" in err:
                    print(f"WARN: {ex_file} :: aha_noticing[{persona}] :: {err}")
                else:
                    failures.append((str(ex_file), f"aha_noticing[{persona}]", err))
            for err in _validate_section("integration", rendered.get("integration", ""), 40, 150, require_aha_terms=False):
                if "missing required callout prefix" in err:
                    print(f"WARN: {ex_file} :: integration[{persona}] :: {err}")
                else:
                    failures.append((str(ex_file), f"integration[{persona}]", err))
    if failures:
        for fpath, sec, msg in failures:
            print(f"{fpath} :: {sec} :: {msg}")
        return 1
    print("OK: exercise sections validated (post-overlay)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
