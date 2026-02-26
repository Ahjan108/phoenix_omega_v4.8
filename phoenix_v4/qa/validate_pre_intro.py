"""
Pre-intro delivery safety gates. Authority: Controlled Intro/Conclusion Variation plan.
Validates resolved pre-intro blocks: no placeholders, no-leak, block order, required blocks when author_id set.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from phoenix_v4.planning.pre_intro_resolver import (
    PRE_INTRO_BLOCK_ORDER,
    REQUIRED_BLOCKS_WHEN_AUTHOR,
)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


# Substrings that must not appear in spoken pre-intro (no-leak).
NO_LEAK_PATTERNS = [
    r"\{\}",           # literal {}
    r"---",            # metadata block boundary
    r"\bid\s*:",        # id:
    r"\bpath\s*:",      # path:
]
# Unresolved placeholders
PLACEHOLDER_PATTERNS = [
    r"\{\{[^}]*\}\}",   # {{...}}
    r"\{[a-zA-Z_]+\}",  # {placeholder}
]
# Markdown artifacts (raw in content)
MARKDOWN_ARTIFACTS = [r"^#+\s", r"\*\*"]


def validate_pre_intro(
    resolved_blocks: dict[str, str],
    author_id: Optional[str] = None,
) -> ValidationResult:
    """
    Validate resolved pre-intro blocks.
    - Unresolved placeholders: {{...}}, {x}, markdown # or **
    - No-leak: {}, ---, id:, path:
    - Block order: keys must follow §23.4 order when present
    - Required blocks when author_id set: narrator_intro, book_title_line, author_intro, author_background, why_this_book, transition_line (series_line optional)
    """
    errors: list[str] = []
    warnings: list[str] = []

    full_text = "\n\n".join(
        resolved_blocks.get(k, "")
        for k in PRE_INTRO_BLOCK_ORDER
        if resolved_blocks.get(k)
    )

    # Unresolved placeholders
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, full_text):
            errors.append(f"Pre-intro contains unresolved placeholder (match: {pat}).")
    for pat in MARKDOWN_ARTIFACTS:
        if re.search(pat, full_text, re.MULTILINE):
            errors.append(f"Pre-intro contains markdown artifact (match: {pat}).")

    # No-leak
    for pat in NO_LEAK_PATTERNS:
        if re.search(pat, full_text):
            errors.append(f"Pre-intro contains internal token / leak (match: {pat}).")

    # No unknown block keys (only §23.4 keys allowed)
    known = set(PRE_INTRO_BLOCK_ORDER)
    for k in resolved_blocks:
        if k not in known:
            errors.append(f"Pre-intro has unknown block key: {k!r}.")

    # Required blocks when author_id set
    if author_id:
        for req in REQUIRED_BLOCKS_WHEN_AUTHOR:
            val = resolved_blocks.get(req)
            if not val or not str(val).strip():
                errors.append(f"Pre-intro required block missing or empty when author_id set: {req!r}.")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
