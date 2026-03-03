#!/usr/bin/env python3
"""
One-shot intake: Ahjan (teacher_id=ahjan) into Teacher Mode V4.
- Ensures SOURCE_OF_TRUTH/teacher_banks/ahjan/ structure
- Copies raw from teachers/ahjan/intake/ if not already present
- Builds KB (tools/teacher_mining/build_kb.py)
Teacher is canonical name "Ahjan"; sources may say "Samvara" or "BD" — same teacher.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INTAKE_SOURCE = REPO_ROOT / "teachers" / "ahjan" / "intake"
TEACHER_ID = "ahjan"
BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / TEACHER_ID


def main() -> int:
    # 1. Ensure dirs
    raw_dir = BANKS / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (BANKS / "kb").mkdir(parents=True, exist_ok=True)
    (BANKS / "doctrine").mkdir(parents=True, exist_ok=True)
    for slot in ("HOOK", "SCENE", "STORY", "EXERCISE", "INTEGRATION", "QUOTE", "TEACHING"):
        (BANKS / "approved_atoms" / slot).mkdir(parents=True, exist_ok=True)
    (BANKS / "candidate_atoms").mkdir(parents=True, exist_ok=True)
    for sub in ("mining_runs", "gap_reports", "approval_logs"):
        (BANKS / "artifacts" / sub).mkdir(parents=True, exist_ok=True)

    # 2. Copy raw from teachers/ahjan/intake if we have source and raw is empty or missing files
    if INTAKE_SOURCE.exists():
        for f in INTAKE_SOURCE.glob("*.rtf"):
            dest = raw_dir / f.name
            if not dest.exists() or dest.stat().st_size != f.stat().st_size:
                shutil.copy2(f, dest)
                print(f"Copied raw: {f.name}")
    else:
        print("Note: teachers/ahjan/intake/ not found; using existing raw/ only.")

    # 3. Build KB
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "teacher_mining" / "build_kb.py"), "--teacher", TEACHER_ID],
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        print("KB build failed.", file=sys.stderr)
        return result.returncode
    print("Ahjan intake complete. Teacher Mode books use teacher_id='ahjan' and teacher_mode=True.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
