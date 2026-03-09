#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass


def run(cmd: list[str], check: bool = True) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({' '.join(cmd)}): {p.stderr.strip()}")
    return p.stdout.strip()


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check)


@dataclass
class Limits:
    max_commits: int = 30
    max_files: int = 300
    max_total_mb: int = 25
    max_single_mb: int = 8


def env_int(name: str, default: int) -> int:
    v = os.environ.get(name, "").strip()
    if not v:
        return default
    try:
        return int(v)
    except Exception:
        return default


def resolve_base_ref() -> str | None:
    up = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False).strip()
    if up:
        return up
    # fallback for new branches with no upstream
    if git("show-ref", "--verify", "--quiet", "refs/remotes/origin/main", check=False) == "":
        # when check=False, stdout is empty regardless return code. use return code style:
        pass
    rc = subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"]).returncode
    if rc == 0:
        return "origin/main"
    return None


def collect_blob_stats(range_expr: str) -> tuple[int, int, int]:
    obj_lines = git("rev-list", "--objects", range_expr, check=False).splitlines()
    if not obj_lines or obj_lines == [""]:
        return (0, 0, 0)

    blob_sizes: list[int] = []
    seen_blob = set()
    for line in obj_lines:
        parts = line.split(" ", 1)
        sha = parts[0].strip()
        if not sha:
            continue
        meta = git("cat-file", "-s", sha, check=False).strip()
        typ = git("cat-file", "-t", sha, check=False).strip()
        if typ != "blob":
            continue
        if sha in seen_blob:
            continue
        seen_blob.add(sha)
        try:
            blob_sizes.append(int(meta))
        except Exception:
            continue

    total_bytes = sum(blob_sizes)
    max_blob = max(blob_sizes) if blob_sizes else 0
    return (len(blob_sizes), total_bytes, max_blob)


def main() -> int:
    ap = argparse.ArgumentParser(description="Block oversized pushes before upload.")
    ap.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = ap.parse_args()

    limits = Limits(
        max_commits=env_int("PUSH_GUARD_MAX_COMMITS", 30),
        max_files=env_int("PUSH_GUARD_MAX_FILES", 300),
        max_total_mb=env_int("PUSH_GUARD_MAX_TOTAL_MB", 25),
        max_single_mb=env_int("PUSH_GUARD_MAX_SINGLE_MB", 8),
    )

    try:
        git("rev-parse", "--is-inside-work-tree")
    except Exception as e:
        print(f"[push-guard] not a git repo: {e}")
        return 2

    base_ref = resolve_base_ref()
    if not base_ref:
        print("[push-guard] no upstream found; allowing push (cannot size diff safely)")
        return 0

    range_expr = f"{base_ref}..HEAD"
    commits = git("rev-list", "--count", range_expr, check=False).strip()
    commit_count = int(commits) if commits else 0

    files_out = git("diff", "--name-only", range_expr, check=False).splitlines()
    file_count = len([x for x in files_out if x.strip()])

    blob_count, total_bytes, max_blob = collect_blob_stats(range_expr)
    total_mb = total_bytes / (1024 * 1024)
    max_blob_mb = max_blob / (1024 * 1024)

    problems: list[str] = []
    if commit_count > limits.max_commits:
        problems.append(f"too many commits ({commit_count}>{limits.max_commits})")
    if file_count > limits.max_files:
        problems.append(f"too many changed files ({file_count}>{limits.max_files})")
    if total_mb > limits.max_total_mb:
        problems.append(f"push payload too large ({total_mb:.1f}MB>{limits.max_total_mb}MB)")
    if max_blob_mb > limits.max_single_mb:
        problems.append(f"single blob too large ({max_blob_mb:.1f}MB>{limits.max_single_mb}MB)")

    summary = (
        f"[push-guard] base={base_ref} commits={commit_count} files={file_count} "
        f"blobs={blob_count} total_mb={total_mb:.1f} max_blob_mb={max_blob_mb:.1f}"
    )

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "base_ref": base_ref,
                    "commits": commit_count,
                    "files": file_count,
                    "blobs": blob_count,
                    "total_mb": round(total_mb, 2),
                    "max_blob_mb": round(max_blob_mb, 2),
                    "limits": limits.__dict__,
                    "problems": problems,
                }
            )
        )
    else:
        print(summary)

    if problems:
        print("[push-guard] BLOCKED:")
        for p in problems:
            print(f"  - {p}")
        print("[push-guard] Split into smaller pushes before retry.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
