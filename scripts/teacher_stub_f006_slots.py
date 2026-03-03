#!/usr/bin/env python3
"""
Generate minimal stub candidate atoms for F006 slot types that teachers may lack:
HOOK, SCENE, REFLECTION, INTEGRATION, COMPRESSION (12 each for 12-ch F006).
Run then: tools/approval/approve_atoms.py --teacher <id> approve-all
"""
from __future__ import annotations

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
CONFIG = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"

F006_SLOTS = ["HOOK", "SCENE", "REFLECTION", "INTEGRATION", "COMPRESSION"]
TARGET_PER_SLOT = 20  # F006 20-ch arc

STUB_BODY = {
    "HOOK": "A moment of pause. What is already here, before we go further.",
    "SCENE": "A brief scene that grounds the teaching in lived experience.",
    "REFLECTION": "A short reflection that ties the practice to what matters.",
    "INTEGRATION": "A closing note to carry this into what comes next.",
    "COMPRESSION": "A distilled takeaway from this section.",
}


def count_approved(teacher_id: str, slot: str) -> int:
    d = BANKS / teacher_id / "approved_atoms" / slot
    if not d.exists():
        return 0
    return sum(1 for f in d.glob("*.yaml") if f.suffix in (".yaml", ".yml"))


def main():
    reg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    teachers = list((reg.get("teachers") or {}).keys())
    for tid in teachers:
        bank = BANKS / tid
        if not bank.exists():
            continue
        cand_root = bank / "candidate_atoms"
        cand_root.mkdir(parents=True, exist_ok=True)
        written = 0
        for slot in F006_SLOTS:
            have = count_approved(tid, slot)
            gap = max(0, TARGET_PER_SLOT - have)
            if gap == 0:
                continue
            slot_dir = cand_root / slot
            slot_dir.mkdir(parents=True, exist_ok=True)
            existing = list(slot_dir.glob("*.yaml"))
            start_idx = len(existing)
            body = STUB_BODY.get(slot, "Stub content for pipeline coverage.")
            for i in range(gap):
                idx = start_idx + i
                atom_id = f"{tid}_{slot}_{idx:03d}_stub"
                data = {
                    "atom_id": atom_id,
                    "body": body,
                    "teacher": {"teacher_id": tid, "source_refs": [{"synthesis_method": "stub_f006"}]},
                }
                path = slot_dir / f"{atom_id}.yaml"
                path.write_text(
                    yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                written += 1
        if written:
            print(f"  {tid}: wrote {written} F006 slot stubs")
    print("Done. Run: tools/approval/approve_atoms.py --teacher <id> approve-all for each teacher.")


if __name__ == "__main__":
    main()
