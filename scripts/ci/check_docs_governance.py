#!/usr/bin/env python3
"""DOCS_INDEX governance checker: enforce rules for documentation index.

Rules:
1. No broken markdown links — every [text](path) link must point to existing file
2. Missing files flagged — detect [anything](path) where path doesn't exist  
3. Last updated date must exist in the file
4. With --check-staleness: warn if Last updated date > 30 days old
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

# Regex to find markdown links: [text](path)
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Regex to find Last updated date: **Last updated:** YYYY-MM-DD
LAST_UPDATED_RE = re.compile(r'(?im)^\*\*Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})\s*$')


def find_repo_root(docs_index_path: Path) -> Path:
    """Find repo root as parent of docs/ directory."""
    if docs_index_path.is_absolute():
        docs_dir = docs_index_path.parent
    else:
        docs_dir = docs_index_path.resolve().parent
    
    # Repo root should be the parent of docs/
    return docs_dir.parent


def _iter_md_links(text: str) -> Iterable[tuple[int, str, str]]:
    """Iterate over markdown links, yielding (line_num, text, target)."""
    for line_num, line in enumerate(text.split('\n'), start=1):
        for m in LINK_RE.finditer(line):
            link_text = m.group(1).strip()
            target = m.group(2).strip()
            
            # Skip empty targets
            if not target:
                continue
            
            # Skip external links (http://, https://, etc.)
            if _is_external(target):
                continue
            
            yield (line_num, link_text, target)


def _is_external(target: str) -> bool:
    """Check if target is an external link (URL, anchor-only, template var)."""
    prefixes = ("http://", "https://", "mailto:", "tel:", "data:", "app://", "vscode://")
    return (
        target.startswith(prefixes) 
        or target.startswith("#")  # anchor-only links
        or "{{" in target 
        or "}}" in target
    )


def resolve_link(docs_dir: Path, target: str) -> Path | None:
    """Resolve a relative link from docs_dir.
    
    Args:
        docs_dir: Directory where DOCS_INDEX.md lives
        target: Link target (relative path, may include anchor)
    
    Returns:
        Resolved Path or None if anchor-only
    """
    # Strip anchor
    no_anchor = target.split("#", 1)[0].strip()
    
    # Empty after stripping anchor means it was anchor-only
    if not no_anchor:
        return None
    
    # Handle absolute-style paths
    if no_anchor.startswith("/"):
        p = Path(no_anchor)
    else:
        # Relative to docs directory
        p = (docs_dir / no_anchor).resolve()
    
    return p


def check_docs_index(docs_index_path: Path, check_staleness: bool = False) -> int:
    """Check DOCS_INDEX.md governance.
    
    Returns:
        0 on success, 1 on failure
    """
    if not docs_index_path.exists():
        print(f"ERROR: DOCS_INDEX.md not found at {docs_index_path}")
        return 1
    
    docs_dir = docs_index_path.parent
    repo_root = find_repo_root(docs_index_path)
    
    try:
        text = docs_index_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: Failed to read {docs_index_path}: {e}")
        return 1
    
    # Check 1: Broken links
    broken_links = []
    for line_num, link_text, target in _iter_md_links(text):
        resolved = resolve_link(docs_dir, target)
        if resolved is None:
            continue
        
        if not resolved.exists():
            broken_links.append((line_num, link_text, target, resolved))
    
    # Check 2: Missing files (already detected by broken links above)
    # The broken_links list contains both cases
    
    # Check 3: Last updated date exists
    last_updated_match = LAST_UPDATED_RE.search(text)
    if not last_updated_match:
        print("DOCS_INDEX governance check FAILED")
        print("  Missing required field:")
        print("    **Last updated:** YYYY-MM-DD header not found")
        if broken_links:
            print("  Broken links (files that don't exist):")
            for line_num, link_text, target, resolved in broken_links:
                print(f"    line {line_num}: [{link_text}]({target})")
        return 1
    
    last_updated_str = last_updated_match.group(1)
    try:
        last_updated_date = datetime.strptime(last_updated_str, "%Y-%m-%d").date()
    except ValueError:
        print("DOCS_INDEX governance check FAILED")
        print(f"  Invalid **Last updated:** date format: '{last_updated_str}'")
        if broken_links:
            print("  Broken links (files that don't exist):")
            for line_num, link_text, target, resolved in broken_links:
                print(f"    line {line_num}: [{link_text}]({target})")
        return 1
    
    # Check 4: Staleness (if requested)
    staleness_warning = None
    if check_staleness:
        today = datetime.now().date()
        age = (today - last_updated_date).days
        if age > 30:
            staleness_warning = f"Last updated {age} days ago (threshold: 30 days)"
    
    # Report results
    if broken_links:
        print("DOCS_INDEX governance check FAILED")
        print("  Broken links (files that don't exist):")
        for line_num, link_text, target, resolved in broken_links:
            print(f"    line {line_num}: [{link_text}]({target})")
        print("  Fix: replace broken links with plain text and mark as backlog items.")
        return 1
    
    if staleness_warning:
        print("DOCS_INDEX governance check WARNING")
        print(f"  {staleness_warning}")
        print(f"  Last updated date: {last_updated_str}")
        return 0  # Warning doesn't fail the check
    
    print("DOCS_INDEX governance check PASSED")
    print(f"  Checked: {docs_index_path.relative_to(repo_root)}")
    print(f"  Link integrity: OK")
    print(f"  Last updated: {last_updated_str}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check DOCS_INDEX.md governance rules"
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Path to DOCS_INDEX.md (default: docs/DOCS_INDEX.md relative to repo root)"
    )
    parser.add_argument(
        "--check-staleness",
        action="store_true",
        help="Warn if Last updated date is > 30 days old"
    )
    
    args = parser.parse_args()
    
    # Determine DOCS_INDEX.md path
    if args.index:
        docs_index_path = args.index.resolve()
    else:
        # Default: look for docs/DOCS_INDEX.md from current working directory
        cwd = Path.cwd()
        
        # Try relative to current directory
        candidate = cwd / "docs" / "DOCS_INDEX.md"
        if candidate.exists():
            docs_index_path = candidate
        else:
            # Try as absolute from /sessions/.../
            # Look for the canonical path
            candidate = Path("/sessions/busy-vibrant-maxwell/mnt/phoenix_omega/docs/DOCS_INDEX.md")
            if candidate.exists():
                docs_index_path = candidate
            else:
                # Fallback to current dir assumption
                docs_index_path = cwd / "docs" / "DOCS_INDEX.md"
    
    return check_docs_index(docs_index_path, check_staleness=args.check_staleness)


if __name__ == "__main__":
    raise SystemExit(main())
