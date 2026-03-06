#!/usr/bin/env python3
"""
Detect add/change/drop events between two git refs using system registry.
Output: artifacts/observability/change_events.jsonl
Authority: docs/CHANGE_OBSERVATION_AND_IMPACT_SPEC.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_registry(repo_root: Path) -> dict:
    import yaml
    reg_path = repo_root / "config" / "governance" / "system_registry.yaml"
    if not reg_path.exists():
        return {"systems": {}}
    return yaml.safe_load(reg_path.read_text()) or {"systems": {}}


def _expand_asset_globs(repo_root: Path, assets: list[str]) -> set[str]:
    out = set()
    for pattern in assets or []:
        if "*" not in pattern:
            p = repo_root / pattern
            if p.exists():
                out.add(pattern)
            continue
        # Simple glob: config/marketing/**/*.yaml -> config/marketing/**/*.yaml
        prefix = pattern.split("*")[0].rstrip("/")
        dir_path = repo_root / prefix
        if not dir_path.is_dir():
            continue
        for f in dir_path.rglob("*"):
            if f.is_file():
                rel = f.relative_to(repo_root)
                out.add(rel.as_posix())
    return out


def _paths_by_system(repo_root: Path, registry: dict) -> dict[str, set[str]]:
    """Map system_id -> set of repo-relative paths that belong to it."""
    by_system: dict[str, set[str]] = {}
    systems = registry.get("systems") or {}
    for sid, meta in systems.items():
        assets = meta.get("assets") or []
        by_system[sid] = _expand_asset_globs(repo_root, assets)
    return by_system


def _git_diff_names(ref_a: str, ref_b: str, repo_root: Path) -> tuple[set[str], set[str], set[str]]:
    """Return (added, changed, dropped) as sets of repo-relative paths."""
    added, changed = set(), set()
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-status", f"{ref_a}...{ref_b}"],
            cwd=str(repo_root),
            text=True,
        )
    except subprocess.CalledProcessError:
        return added, changed, set()
    for line in out.strip().splitlines():
        if not line:
            continue
        status = line[0]
        path = line[1:].strip().split("\t")[0]
        if status == "A":
            added.add(path)
        elif status in ("M", "T"):
            changed.add(path)
        elif status == "D":
            pass  # dropped: we'll infer from ref_b
    # Dropped = in ref_a but not in ref_b (list tree at ref_a, diff)
    try:
        tree = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", ref_b],
            cwd=str(repo_root),
            text=True,
        )
        at_b = set(tree.strip().splitlines())
    except subprocess.CalledProcessError:
        at_b = set()
    try:
        tree_a = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", ref_a],
            cwd=str(repo_root),
            text=True,
        )
        at_a = set(tree_a.strip().splitlines())
    except subprocess.CalledProcessError:
        at_a = set()
    dropped = at_a - at_b
    return added, changed, dropped


def _path_to_system_ids(path: str, path_to_systems: dict[str, list[str]]) -> list[str]:
    """Which system_ids claim this path (path may be under multiple assets)."""
    return path_to_systems.get(path, [])


def main() -> int:
    ap = argparse.ArgumentParser(description="Git diff + registry → change_events.jsonl")
    ap.add_argument("--base", default="HEAD", help="Base ref (e.g. main)")
    ap.add_argument("--head", default="HEAD", help="Head ref (e.g. branch)")
    ap.add_argument("--out", default=None, help="Output JSONL path (default: artifacts/observability/change_events.jsonl)")
    args = ap.parse_args()

    registry = _load_registry(REPO_ROOT)
    by_system = _paths_by_system(REPO_ROOT, registry)
    # Invert: path -> [system_ids]
    path_to_systems: dict[str, list[str]] = {}
    for sid, paths in by_system.items():
        for p in paths:
            path_to_systems.setdefault(p, []).append(sid)

    added, changed, dropped = _git_diff_names(args.base, args.head, REPO_ROOT)

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "observability" / "change_events.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    events = []
    for path in sorted(added):
        system_ids = _path_to_system_ids(path, path_to_systems)
        if not system_ids:
            system_ids = ["_unregistered"]
        events.append({
            "kind": "added",
            "path": path,
            "system_ids": system_ids,
            "scope": system_ids[0] if system_ids else None,
        })
    for path in sorted(changed):
        system_ids = _path_to_system_ids(path, path_to_systems)
        if not system_ids:
            system_ids = ["_unregistered"]
        events.append({
            "kind": "changed",
            "path": path,
            "system_ids": system_ids,
            "scope": system_ids[0] if system_ids else None,
        })
    for path in sorted(dropped):
        system_ids = _path_to_system_ids(path, path_to_systems)
        if not system_ids:
            system_ids = ["_unregistered"]
        events.append({
            "kind": "dropped",
            "path": path,
            "system_ids": system_ids,
            "scope": system_ids[0] if system_ids else None,
        })

    with open(out_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    print(f"Wrote {len(events)} events to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
